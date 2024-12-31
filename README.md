<img src="assets/logo.png" alt="Logo" width="200">

# 🎙️ Podcastify - A Document and Story Podcast Creator

Transform documents into engaging podcasts or create random story podcasts using personas with just a few clicks!

---

## 🌟 Features

- **Upload Documents**: Generate podcasts based on your document's content.
- **Storytelling Personas**: Choose from pre-defined personas for unique narration styles.
- **Audio Generation**: High-quality podcast audio created using ElevenLabs.
- **Dynamic Transcript**: Easily readable podcast-style transcripts.

---

## 🎥 UI in Action

### Upload a Document
![UI Upload](assets/ui_upload.png)

### Generated Podcast Transcript
![UI Transcript](assets/ui_transcript.png)

### Podcast Audio Output
![UI Audio](assets/ui_audio.png)

---

## 🎧 Sample Audio Outputs

### Sample 1: Generated Podcast for a Technical Document


---

### Sample 2: Story Podcast - Magical Storyteller Persona


---

### Sample 3: Comedy Podcast - Stand-Up Comedian Persona


---

### Sample 4: Inspirational Story - Fitness Coach Persona


---

## 🚀 Getting Started

### 1️⃣ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/document-podcast-creator.git
   cd podcastify
    ```

2. Create a virtual environment and activate it:
    ```bash
   python3 -m venv venv
   source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
     ```

### 2️⃣ Setup Environment Variables

Create a .env file in the root directory with the following content:

   ```bash
    # OpenAI API Key
   OPENAI_API_KEY=<your_openai_api_key>
   
   # ElevenLabs API Key
   ELEVENLABS_API_KEY=<your_elevenlabs_api_key>
   
   # OpenAI Model Settings
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_MAX_TOKENS=1500
   OPENAI_TEMPERATURE=0.7
   ```

---

### 3️⃣ Run the Application

1.	Launch the application:
   ```bash
    streamlit run app.py
   ```
2. Open your browser and navigate to the provided local URL (e.g., http://127.0.0.1:7860/). 
3. Upload a document or leave it blank, choose a persona, and click **Generate Podcast**.

# 🤝 Contribution

Please fork this repository, make your changes, and submit a pull request. For major changes, open an issue first to discuss what you’d like to change.

---

# 🛠️ Troubleshooting

•	Missing API Keys: Ensure OPENAI_API_KEY and ELEVENLABS_API_KEY are correctly set in the .env file.
•	Audio Generation Issues: Verify that ElevenLabs API access is active.
•	UI Not Loading: Ensure all dependencies are installed and the correct Python environment is activated.

---

# 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.