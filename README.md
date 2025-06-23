# Building Asynchronous AI Agents with Strands Agents SDK

## Table of Contents
- [Introduction](#introduction)
- [Workshop Scenario](#workshop-scenario)
- [What You'll Build](#what-youll-build)
- [Architecture Overview](#architecture-overview)
- [Workshop Structure](#workshop-structure)
- [Getting Started](#getting-started)
- [Resources](#resources)

## Introduction

Welcome to this hands-on workshop on building asynchronous AI agents using the Strands Agents SDK! Throughout this workshop, you'll learn how to design, implement, and deploy intelligent agents that can operate asynchronously, maintain state across executions, and collaborate with other agents to accomplish complex tasks.

### What You'll Build

We'll be creating a marketing automation system for UniTok - a fictional social media platform for renting unicorns. By the end of this workshop, you'll have built a complete system of asynchronous agents that can:

1. Generate engaging social media posts
2. Process tasks asynchronously
3. Handle long-running operations with state persistence
4. Collaborate in a multi-agent system with specialized roles

### Architecture Pattern

This workshop focuses on an event-driven, serverless architecture pattern that enables truly asynchronous agent execution. The key components include:

- **Strands Agents SDK**: Provides the foundation for building intelligent agents with access to tools and LLM capabilities
- **AWS Lambda**: Serverless compute for running our agents
- **Amazon SQS**: Message queuing service for task management between agent executions
- **Amazon DynamoDB**: NoSQL database for persisting agent state
- **AWS SNS**: Notification service for human-in-the-loop approvals

### Why This Architecture?

Traditional agent implementations often run synchronously, blocking execution until completion. This approach has several limitations:

1. **Timeout constraints**: Synchronous executions are limited by platform timeouts (e.g., AWS Lambda's 15-minute limit)
2. **Resource inefficiency**: Compute resources remain allocated during waiting periods
3. **Limited scalability**: Difficult to handle concurrent requests efficiently
4. **Fragility**: Long-running processes are vulnerable to interruptions

Our asynchronous architecture addresses these challenges by:

1. **Breaking tasks into discrete steps**: Agents can pause and resume execution
2. **Persisting state**: Saving progress in Amazon DynamoDB allows for continuity across executions
3. **Event-driven processing**: Tasks progress only when needed, optimizing resource usage
4. **Resilience**: System can recover from failures at any stage

### Workshop Structure

The workshop is divided into four progressive labs:

1. **Lab 1**: Build a synchronous post generator agent for generating UniTok marketing posts
2. **Lab 2**: Convert post generator agent to an asynchronous agent using AWS Lambda and Amazon SQS
3. **Lab 3**: Implement long-running tools with human approval workflow
4. **Lab 4**: Create a multi-agent system with specialized roles

Each lab builds upon the previous one, introducing more sophisticated patterns.

## Getting Started

1. Complete the [Lab 0 Prerequisites](labs/lab_0/README.md)
2. Open `labs/lab_1/lab_1_notebook.ipynb` in your VSCode environment
3. Follow the step-by-step instructions in each lab

Let's get started!

### Prerequisites

- Basic Python programming knowledge
- Familiarity with AWS services (Lambda, SQS, DynamoDB)
- (If not at an AWS event) AWS account with appropriate permissions

## Resources

- [Strands Agents SDK Documentation](https://strandsagents.com/latest/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
