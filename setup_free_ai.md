# Free AI Setup Guide - Ollama Only

## Step 1: Install Ollama

1. Go to https://ollama.ai
2. Download and install Ollama for Windows
3. Restart your computer

### Step 2: Download a Model

**Choose based on your storage/RAM:**

**For smaller storage/RAM (recommended):**

```bash
ollama run llama3.2:1b
```

This downloads a 1.3GB model (much smaller!)

**For medium performance:**

```bash
ollama run llama3.1:8b
```

This downloads a 4.7GB model (good balance)

**For maximum performance (if you have space):**

```bash
ollama run llama3.1
```

This downloads a 4.9GB model (best quality)

### Step 3: Test Ollama

In a new terminal window:

```bash
ollama list
```

You should see `llama3.1` in the list.

### Alternative Models (if you want smaller/different models):

```bash
ollama run llama3.1:8b    # 8B parameters (smaller, faster)
ollama run codellama      # Good for code
ollama run mistral        # Good alternative
```

## Option 2: Hugging Face (Free with Rate Limits)

### Step 1: Get Free Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (free account)
3. Copy the token

### Step 2: Add to Environment

Create or edit your `.env` file:

```
HUGGINGFACE_TOKEN=your_token_here
```

## Testing Your Setup

Run your application:

```bash
python main2.py
```

The code will automatically:

1. Try Ollama first (if running)
2. Fall back to Hugging Face (if token provided)
3. Show helpful error messages if neither works

## Troubleshooting

### Ollama Issues:

- Make sure Ollama is running: `ollama serve`
- Check if model is downloaded: `ollama list`
- Try a smaller model: `ollama run llama3.1:8b`

### Memory Requirements:

- Llama 3.1 (8B): ~8GB RAM recommended
- Llama 3.1 (70B): ~40GB RAM (not recommended for most PCs)
- For lower-end PCs, try: `ollama run tinyllama`

### Performance:

- First response will be slower (model loading)
- Subsequent responses will be faster
- Consider keeping Ollama running in background
