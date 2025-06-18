# Building a Synchronous Marketing Agent for UniTok

## Introduction

In this first lab, we'll build a synchronous agent using the Strands Agents SDK to generate marketing content for UniTok, our fictional unicorn rental social media platform. This lab establishes the foundation for our agent architecture before we transform it into an asynchronous system in later labs.

## Lab Objectives

By the end of this lab, you will:
- Understand the basic structure of a Strands Agent
- Configure an agent with custom tools and instructions
- Implement a marketing post generator for UniTok
- Test your agent with various marketing prompts

## UniTok Platform Overview

For this workshop, we'll be working with the UniTok platform - a fictional social media app where users can browse, rent, and share experiences with unicorns. The UniTok backend API and infrastructure are already deployed and running - you don't need to worry about setting up these resources as they're outside the scope of this workshop.

The UniTok API provides endpoints for:
- Publishing posts to the platform
- Retrieving unicorn data and statistics
- Accessing user engagement metrics

We'll interact with these existing endpoints through our agent's tools.

## Lab Structure

This lab consists of the following components:

1. **Agent Configuration**
   - Setting up the Strands Agent with appropriate instructions
   - Defining the agent's persona as a marketing specialist

2. **Tool Implementation**
   - Creating the `publish_post` tool to interface with UniTok's API

3. **Agent Execution**
   - Processing user prompts to generate marketing content
   - Using the LLM to craft engaging posts based on instructions

## Key Concepts

### Strands Agents SDK

The Strands Agents SDK provides a framework for building AI agents that can:
- Process natural language instructions
- Access and use tools to interact with external systems
- Maintain context throughout a conversation
- Generate appropriate responses based on their configuration

### Agent Instructions

Our marketing agent will be configured with specific instructions that define:
- Its role as a UniTok marketing specialist
- Guidelines for creating engaging content
- Tone and style appropriate for the UniTok platform
- Constraints and best practices for social media marketing

We will use the following instructions as a `system_prompt` for the agent:
```
You are a creative social media manager for Unicorn Rentals, a company that offers unicorns for rent that kids and grown-ups can play with.

Your task is to create engaging social media posts for UniTok, our unicorn-themed social media platform. 

Important information about Unicorn Rentals:
- We offer unicorns in various colors: pink, blue, purple, green, yellow, and rainbow (our most popular)
- Our new product feature allows customers to pick their favorite color unicorn to rent (default: rainbow)
- Our target audience includes families with children, fantasy enthusiasts, and event planners
- Our brand voice is magical, playful, and family-friendly

When creating posts:
- Keep content family-friendly and positive
- Highlight the magical experience of spending time with unicorns
- Mention the new color selection feature when appropriate
- Use emojis sparingly but effectively
- Keep posts between 50-200 characters for optimal engagement

After generating the post, you can publish directly to UniTok.
```

After crafting instructions for the agent, creation of an `Agent` with Strands Agents is straight forward:

```
from strands import Agent

# Initialize the model
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    # Add any additional model configuration here
)

# Create the agent
post_generator_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    tools=[publish_post],
)
```

### Tools

Tools are functions that allow our agent to interact with external systems. In this lab, we'll implement:

- `publish_post`: A tool that sends generated content to the UniTok platform

With Strands Agents a `tool` can be easily implemented with the help of `@tool` decorator
```
from strands import tool
@tool
def publish_post(
    content: str, 
    author: str = "Unicorn Rentals", 
    unicorn_color: str = "rainbow", 
    image_url: str = None) -> str:
    """
    Publish a post to the UniTok social media platform.
    
    Args:
        content (str): The text content of the post.
        author (str, optional): The author of the post. Defaults to "Unicorn Rentals".
        unicorn_color (str, optional): The color of the unicorn. Choose from: pink, blue, purple, green, yellow, or rainbow. Defaults to "rainbow".
        image_url (str, optional): URL to an image to include with the post. Defaults to None.
        
    Returns:
        str: A message indicating the post was published successfully, or an error message.
    """

    # Implementation of the tool
```

Strands Agents automatically translates the following to a valid `ToolSpec`: 
- Function parameters (`content, author, unicorn_color, image_url`)
- Parameter types (`str`)
- Required vs optional parameters (`[content], {author, unicorn_color, image_url}`)
- Description of the tool from the doc string (`Publish a post to the UniTok social media platform.`)
- Description of each parameter from doc string 

Additionally Strands Agents SDK automatically handles the returned value and correctly packages it for the agent to parse it appropriately.

> Read more about how to implement tools with Strands Agents [here](https://strandsagents.com/latest/user-guide/concepts/tools/tools_overview/).


## Getting Started

To begin this lab:

1. Open the `lab_1_notebook.ipynb` file in your environment
2. Follow the step-by-step instructions to build your marketing agent
3. Test your agent with the provided sample prompts
4. Experiment with different marketing scenarios

Remember that in this first lab, we're building a synchronous agent - it will process requests and generate responses in a single execution flow. In the next lab, we'll transform this into an asynchronous architecture.

Let's start building our UniTok marketing post generator agent!