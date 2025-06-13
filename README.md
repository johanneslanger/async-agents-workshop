# Async Agents Workshop

This repository contains materials for the "Building Advanced Agents with Strands SDK" workshop. Participants will learn how to build and deploy sophisticated AI agents using the Strands SDK in a practical, hands-on scenario.

## Workshop Scenario

We are a marketing team at **Unicorn-Rentals.AI** - a company that offers unicorns for rent that kids and grown-ups can play with. We are planning to launch a new product feature which allows customers to pick their favorite color of unicorn to rent. Our goal is to automate the social media launch using AI agents.

## Learning Objectives

By the end of this workshop, participants will be able to:

- Create and deploy basic AI agents using Strands SDK
- Implement multi-agent architectures with specialized roles
- Add human-in-the-loop approval workflows
- Build a complete social media campaign management system with multiple coordinated agents
- Integrate agents with external APIs and services


## Workshop Modules

### Module 1: Building Your First Agent
Create a social media post generator agent for "UniTok" that assists social media managers in creating engaging content.
- Implement a custom tool for publishing posts to the UniTok API
- Configure the agent with a specialized system prompt
- Test the agent's ability to generate and publish unicorn-themed content

### Module 2: Multi-Agent - Agent as Tool Pattern
Implement an evaluator agent to ensure posts adhere to brand guidelines before publishing.
- Create a second agent specialized in content evaluation
- Configure the post generator to use the evaluator as a tool
- Implement feedback loops between agents

### Module 3: Adding Human in the Loop Steps
Add approval workflows where human team members can review, approve, reject, or request changes to agent-generated content.
- Implement approval checkpoints in the agent workflow
- Create interfaces for human feedback
- Configure agents to incorporate human feedback

### Module 4: Creating a Social Media Campaign Manager
Build a supervisor campaign manager that coordinates multiple specialized agents to execute a complete social media campaign.
- Design a hierarchical agent structure
- Implement task delegation and coordination
- Create monitoring and reporting capabilities

## Project Structure

```
/
├── notebooks/                  # Jupyter notebooks for workshop modules
│   ├── module1/               # First module - Basic agent implementation
│   │   └── post_generator_agent.ipynb
│   └── requirements.txt       # Python dependencies for notebooks
│
├── unitok/                    # UniTok social media platform
│   ├── backend/               # Backend services
│   │   └── functions/         # Lambda functions
│   │       ├── get-posts/     # Retrieves posts from DynamoDB
│   │       └── publish-post/  # Creates new posts in DynamoDB
│   │
│   ├── frontend/              # React-based web application
│   │   ├── public/            # Static assets
│   │   └── src/               # React components and logic
│   │       ├── components/    # UI components (Feed, Post, Header)
│   │       └── App.jsx        # Main application component
│   │
│   └── infrastructure/        # AWS CDK infrastructure code
│       ├── bin/               # CDK app entry point
│       └── lib/               # Stack definitions
```

## Setup Instructions

### Prerequisites
- AWS Account with appropriate permissions
- Node.js and npm installed
- Python 3.11 or higher
- AWS CLI configured with your credentials

### Installation Steps

1. Clone this repository
   ```
   git clone <repository-url>
   cd async-agents-workshop
   ```

2. Install frontend dependencies
   ```
   cd unitok/frontend
   npm install
   ```

3. Install infrastructure dependencies
   ```
   cd ../infrastructure
   npm install
   ```

4. Deploy the infrastructure
   ```
   cd unitok/infrastructure
   cdk deploy
   ```

6. If you want to test the frontend locally 
   - Copy the API endpoint from the CDK output
   - Update the `unitok/frontend/public/config.json` file with the API endpoint

7. Follow the module notebooks in sequence
   - Start with `notebooks/module1/post_generator_agent.ipynb`


## Resources

- [Strands SDK Documentation](https://strandsagents.com/latest/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)

