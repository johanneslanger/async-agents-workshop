#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import 'source-map-support/register';
import { UniTokStack } from '../lib/unitok-stack';

const app = new cdk.App();

// Create the unified stack
const unitokStack = new UniTokStack(app, 'UniTokStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1' 
  },
  description: 'Unified stack for UniTok social media platform',
});

// Add tags to all resources
cdk.Tags.of(app).add('Project', 'UniTok');
cdk.Tags.of(app).add('Workshop', 'AsyncAgentsWorkshop');
