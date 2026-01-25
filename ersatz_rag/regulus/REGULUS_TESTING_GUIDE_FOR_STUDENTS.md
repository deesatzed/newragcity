# How to Test Regulus: A Guide for Young Coders

Hey there! Welcome to the Regulus project. You're about to test a cool AI chatbot designed to be an expert on company rules. Think of it as a super-smart assistant that can answer any question about a company's policies, like their vacation rules or internet usage policy.

This guide will walk you through how to download it, set it up, and run a demo, explaining each step along the way.

---

### Step 1: Get the Code from GitHub

First things first, you need to get a copy of the Regulus project on your computer. We'll use a tool called `git` to do this. If you don't have git, you can easily install it for your system (macOS, Windows, or Linux).

Open your terminal (or Command Prompt on Windows) and run this command:

```bash
git clone https://github.com/deesatzed/Regulus.git
```

This command downloads the entire `Regulus` project into a new folder on your computer. Once it's done, navigate into the project folder:

```bash
cd Regulus
```

Awesome! You now have the code.

---

### Step 2: What You'll Need (The Prerequisites)

Like any cool project, Regulus needs a few things to work:

1.  **Python**: Regulus is written in Python. You'll need Python 3.10 or newer. You can check your version by typing `python3 --version` in your terminal.
2.  **A Code Editor**: A tool to look at the code, like [Visual Studio Code](https://code.visualstudio.com/) (it's free!).
3.  **An API Key**: This is like a secret password that lets our program talk to a powerful AI model online. The AI helps Regulus understand questions and find the best answers. You can get a free one from a service like [OpenRouter](https://openrouter.ai/).

Once you have your API key, you need to tell your computer about it. In your terminal, run this command (replace `your-api-key-here` with your actual key):

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

**Heads up**: You'll need to run this `export` command every time you open a new terminal window to work on the project.

---

### Step 3: Set Up Your Project Environment

When working on a Python project, it's a great habit to create a **virtual environment**. Think of it as a clean, separate workspace just for this project. It keeps all the project's tools (called dependencies) organized and prevents them from messing with other Python projects on your computer.

Let's set one up. Make sure you are inside the `regulus/backend` folder.

```bash
# Navigate to the backend folder from the main Regulus directory
cd backend

# Create a virtual environment named '.venv'
python3 -m venv .venv

# Activate it (this turns it on)
source .venv/bin/activate
```

After you activate it, you'll see `(.venv)` at the beginning of your terminal prompt. This means you're in the zone!

Now, let's install all the tools Regulus needs. They are listed in a file called `pyproject.toml`.

```bash
# Install all the project's dependencies from the current directory
pip install -e .
```

This might take a few minutes. Once it's done, your project is all set up and ready to go!

---

### Step 4: Run the Demo!

The moment of truth! The project comes with a special script called `complete_demo.py` that shows off everything Regulus can do. This new version is a true live demo: it processes a real document and builds a search index from scratch right before your eyes!

Make sure you are still in the `regulus/backend` folder with your virtual environment active, and run this command:

```bash
python3 complete_demo.py
```

#### What to Look For in the Output:

You'll see a lot of text, but here's what it all means:

1.  **Live Indexing**: The script will first find the `sample_policy.pdf` file, process it, and build a new search index in real-time.
2.  **The Query**: The demo will then ask a series of questions about the policy, like *"What is the purpose of this policy?"*
3.  **Enhanced Hybrid Search**: This is the cool part! Regulus uses a powerful search method that combines a few techniques:
    *   **Vector Search**: Finds text that is semantically similar (matches the meaning) to your question.
    *   **Lexical Search**: Finds text that contains the exact keywords from your question.
    *   **Reranking**: A final AI step that looks at the top results and puts the most relevant one at the very top.
4.  **Calibrated Confidence**: For the best answer, you'll see a confidence breakdown from the `deepConf` system:
    *   `Original Confidence`: The AI's initial guess of how sure it is.
    *   `Calibrated Confidence`: A smarter, adjusted score based on historical performance. This is the one to trust!
    *   `Uncertainty Estimate`: How much doubt the AI has. A lower number is better.
    *   `Relevance`: Does it contain the right keywords?
5.  **The Best Result**: Finally, it will show you the best answer it found and a preview of the text from the policy document.

---

### Step 5: What's Next? Explore and Experiment!

Now that you've run the demo, you can start exploring. Here are a few ideas:

*   **Change the Queries**: Open the `regulus/backend/complete_demo.py` file in your code editor. Find the `test_queries` list and try adding your own questions about an AI policy!
*   **Look at the Code**: Check out `three_approach_integration.py`. This is the main file where all the AI magic happens. See if you can follow the logic of the `broad_then_deep_search` function.

Congratulations! You've successfully downloaded, set up, and tested a real-world AI project. Welcome to the world of AI engineering!
