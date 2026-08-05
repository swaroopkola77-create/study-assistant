# 📚 AI Study Assistant

An AI-powered Study Assistant built with **Python**, **Gradio**, and **Google GenAI**. The application provides an interactive chat interface where users can ask study-related questions and receive clear, AI-generated explanations in real time.

## 🚀 Features

- 🤖 AI-powered study assistance
- 💬 Interactive Gradio web interface
- 📖 Clear explanations for academic questions
- ⚡ Fast and lightweight application
- 🌐 Ready for deployment on Render
- 🔒 Secure API key management using environment variables

## 🛠️ Tech Stack

- Python
- Gradio
- Google GenAI
- Git & GitHub
- Render

## 📂 Repository Structure

```
.
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment configuration
└── README.md           # Project documentation
```

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set the API Key

Create an environment variable:

```text
GOOGLE_API_KEY=your_google_genai_api_key
```

## ▶️ Run the Application

```bash
python app.py
```

The Gradio interface will start locally and open in your browser.

## 🌐 Deployment

This project is configured for deployment on **Render**.

1. Push the project to GitHub.
2. Create a new Web Service on Render.
3. Connect your GitHub repository.
4. Add the `GOOGLE_API_KEY` environment variable.
5. Deploy the application.

## 📖 How It Works

1. The user enters a study-related question.
2. The question is sent to the Google GenAI model.
3. The AI generates a response.
4. Gradio displays the answer in an easy-to-use chat interface.

## 🔮 Future Enhancements

- Conversation history
- PDF document support
- Quiz generation
- Flashcard generation
- Subject-specific assistants
- Voice interaction
- Multi-language support

## 📄 License

This project is intended for learning and educational purposes.

## 👨‍💻 Author

Developed as a learning project to explore AI application development using **Gradio** and **Google GenAI**.

⭐ If you found this project helpful, consider starring the repository!
