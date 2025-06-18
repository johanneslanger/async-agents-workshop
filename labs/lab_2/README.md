# Converting to an Asynchronous Agent Architecture

## Introduction

In Lab 1, we built a synchronous marketing agent that generates posts for UniTok. While functional, this approach has limitations when dealing with complex workflows or long-running processes. In this lab, we'll transform our agent into an asynchronous system using AWS Lambda and Amazon SQS, enabling it to handle tasks more efficiently and reliably.

## Lab Objectives

By the end of this lab, you will:
- Understand the benefits of asynchronous agent architectures
- Package your Strands Agent into an AWS Lambda function
- Configure SQS for task management
- Test the asynchronous execution flow

## Why Go Asynchronous?

Synchronous agents face several limitations:
- **Execution time constraints**: Cloud function platforms typically have timeout limits (e.g., 15 minutes for AWS Lambda)
- **Resource inefficiency**: Compute resources remain allocated during waiting periods
- **Poor scalability**: Difficult to handle concurrent requests efficiently
- **Vulnerability to interruptions**: Long-running processes can fail if connections drop

By converting to an asynchronous architecture, we address these challenges through:
- **Event-driven execution**: The agent only runs when there's work to do
- **Decoupled components**: Tasks and processing are separated for better resilience
- **Scalable processing**: Multiple agent instances can process tasks in parallel
- **Improved fault tolerance**: Failed tasks can be retried without losing progress

## Architecture Components

Our asynchronous architecture consists of these key components:

1. **SQS Queue (`post-generator-task-queue`)**: 
   - Stores tasks waiting to be processed
   - Provides at-least-once delivery guarantees
   - Handles message visibility and dead-letter scenarios

2. **Lambda Function (`post_generator_agent`)**:
   - Contains our Strands Agent code
   - Triggered by messages in the SQS queue
   - Processes tasks and publishes results
   - Returns quickly, regardless of the underlying task complexity

3. **Task Structure**:
   - JSON payloads containing user prompt/request
        ```json
        {
            "type": "new",
            "body": {
                "task": "Create a post highlighting our pink unicorns and what makes them special."
            }
        }
        ```
    The above task structure is delibarately kept simple and can be extended in production scenarios with:
   - Task ID for tracking
   - Current state of processing
   - Any additional context needed for execution

## Lab Structure

This lab consists of the following components:

1. **Lambda Function Setup**
   - Packaging our agent code for Lambda deployment
   - Configuring environment variables and permissions

2. **SQS Configuration**
   - Setting up the `post-generator-task-queue`
   - Configuring message retention and visibility timeouts
   - Configure a Lambda trigger to invoke the Lambda function when the new task arrives

3. **Testing the Asynchronous Flow**
   - Submitting tasks to the queue
   - Analyzing results in UniTok website

## Implementation Details

### Task Processing Flow

1. A new marketing task is added to the `post-generator-task-queue`
2. The SQS trigger invokes our `post_generator_agent` Lambda function
3. The Lambda function extracts the task details from the event
4. Our agent processes the task using the Strands Agents SDK
5. The agent publishes the post to UniTok (if appropriate)
6. The Lambda function completes, and SQS removes the processed message

### Error Handling

Our asynchronous architecture needs robust error handling:

- **Message visibility timeout**: If processing fails, the message becomes visible again in the queue
- **Dead-letter queue**: After multiple failed attempts, messages move to a dead-letter queue for debugging
- **Error logging**: Detailed error information is captured for troubleshooting via CloudWatch logs

## Getting Started

To begin this lab:

1. Open the `lab_2_notebook.ipynb` file in your environment
2. Follow the step-by-step instructions to convert your agent to an asynchronous architecture
3. Deploy the Lambda function and configure the SQS queue
4. Test the asynchronous flow with sample marketing requests

By the end of this lab, you'll have a functional asynchronous agent that can process marketing tasks for UniTok through a queue-based architecture, setting the foundation for more complex workflows in the next labs.