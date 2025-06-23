import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { DeployTimeSubstitutedFile } from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as fs from 'fs';
import * as path from 'path';

export class UniTokStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 1. Database resources
    const postsTable = this.createDatabaseResources();
    
    // 2. API resources (depends on database)
    const apiEndpoint = this.createApiResources(postsTable);
    
    // 3. Frontend resources (depends on API)
    this.createFrontendResources(apiEndpoint);

    const strandsLayer = this.createStrandsLambdaLayer();
    
    // 4. Outputs
    this.createOutputs(postsTable, apiEndpoint,strandsLayer);
  }

  /**
   * Creates the DynamoDB table for storing posts
   */
  private createDatabaseResources(): dynamodb.Table {
    // Create DynamoDB table for posts
    const postsTable = new dynamodb.Table(this, 'PostsTable', {
      partitionKey: { name: 'postId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For demo purposes only
      pointInTimeRecovery: true,
    });

    // Add GSI for timestamp to enable sorting by most recent
    postsTable.addGlobalSecondaryIndex({
      indexName: 'TimestampIndex',
      partitionKey: { name: 'dummy', type: dynamodb.AttributeType.STRING }, // Always 'POST'
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    return postsTable;
  }

  /**
   * Creates the API Gateway and Lambda functions
   */
  private createApiResources(postsTable: dynamodb.Table): string {
    // Create Lambda function for publishing posts
    const publishPostFunction = new lambda.Function(this, 'PublishPostFunction', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../backend/functions/publish-post'), ),
      environment: {
        POSTS_TABLE: postsTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    });

    // Create Lambda function for getting posts
    const getPostsFunction = new lambda.Function(this, 'GetPostsFunction', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../backend/functions/get-posts')),
      environment: {
        POSTS_TABLE: postsTable.tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
    });

    // Grant permissions to Lambda functions
    postsTable.grantReadWriteData(publishPostFunction);
    postsTable.grantReadData(getPostsFunction);

    // Create API Gateway
    const api = new apigateway.RestApi(this, 'UniTokApi', {
      restApiName: 'UniTok API',
      description: 'API for UniTok social media platform',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // Create API resources and methods
    const postsResource = api.root.addResource('posts');
    
    // GET /posts
    postsResource.addMethod('GET', new apigateway.LambdaIntegration(getPostsFunction));
    
    // POST /posts
    postsResource.addMethod('POST', new apigateway.LambdaIntegration(publishPostFunction));

    return api.url;
  }

  /**
   * Creates the S3 bucket and CloudFront distribution for the frontend
   */
  private createFrontendResources(apiEndpoint: string): void {
    // Create S3 bucket for website hosting
    const websiteBucket = new s3.Bucket(this, 'WebsiteBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For demo purposes only
      autoDeleteObjects: true, // For demo purposes only
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create CloudFront distribution
    const distribution = new cloudfront.Distribution(this, 'Distribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(websiteBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
    });

    // Use the build directory directly (assuming it exists)
    const buildPath = path.join(__dirname, '../../frontend/build');
    
    // Deploy website content to S3 (excluding config.json)
    new s3deploy.BucketDeployment(this, 'DeployWebsite', {
      sources: [s3deploy.Source.asset(buildPath)],
      destinationBucket: websiteBucket,
      distribution,
      distributionPaths: ['/*'],
      exclude: ['config.json'], // Exclude config.json from this deployment
    });

    // Create a template config.json file with placeholders
    const configTemplatePath = path.join(__dirname, '../../frontend/config-template.json');
    fs.writeFileSync(
      configTemplatePath,
      JSON.stringify({ apiEndpoint: '{{ apiEndpoint }}' })
    );
    
    // Use DeployTimeSubstitutedFile to deploy with substitutions
    new DeployTimeSubstitutedFile(this, 'DeployConfig', {
      source: configTemplatePath,
      destinationBucket: websiteBucket,
      destinationKey: 'config.json',
      substitutions: {
        apiEndpoint: apiEndpoint, // This will be substituted at deployment time
      },
    });

    // Store the distribution domain name for outputs
    this.distributionDomainName = distribution.distributionDomainName;

    //Layer to deploy strands based agents used throughout the workshop
       
  }

  /**
     * Creates the S3 bucket and CloudFront distribution for the frontend
     */
  private createStrandsLambdaLayer(): lambda.LayerVersion {
  
     return new lambda.LayerVersion(this, 'StrandsLayer', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../layers/strands/'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_11.bundlingImage,
          command: [
            'bash', '-c', [
              'pip install --no-cache-dir -r requirements.txt --only-binary=:all: --platform manylinux2014_x86_64 -t /asset-output/python',
              'cp -r . /asset-output'
            ].join(' && ')
          ],
        },
      }),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
      compatibleArchitectures: [lambda.Architecture.ARM_64],
      description: 'Dependencies for Strands Agents',
    });
  }
  /**
   * Creates the stack outputs
   */
  private createOutputs(postsTable: dynamodb.Table, apiEndpoint: string,strandsLayer: lambda.LayerVersion): void {

    new cdk.CfnOutput(this, 'Strandslayer', {
      value: strandsLayer.layerVersionArn,
      description: 'The name of the posts table',
    });

    // Database outputs
    new cdk.CfnOutput(this, 'PostsTableName', {
      value: postsTable.tableName,
      description: 'The name of the posts table',
    });

    new cdk.CfnOutput(this, 'PostsTableArn', {
      value: postsTable.tableArn,
      description: 'The ARN of the posts table',
    });

    // API outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: apiEndpoint,
      description: 'The endpoint URL of the UniTok API',
    });

    // Frontend outputs
    new cdk.CfnOutput(this, 'DistributionDomainName', {
      value: this.distributionDomainName,
      description: 'The domain name of the CloudFront distribution',
    });
  }

  // Property to store the CloudFront distribution domain name
  private distributionDomainName: string;
}
