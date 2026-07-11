import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf(filename: str = "sample_ai.pdf") -> None:
    """Generates a sample PDF file with structured text for testing SmartNotes AI."""
    print(f"Generating test PDF: {filename}...")
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1: Introduction to AI
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 720, "Introduction to Artificial Intelligence")
    c.setFont("Helvetica", 11)
    # Simple educational paragraphs with definitions for rule-based extraction
    c.drawString(50, 680, "Artificial intelligence is a branch of computer science that builds smart machines.")
    c.drawString(50, 660, "Intelligence refers to the ability to learn, reason, and solve complex problems.")
    c.drawString(50, 640, "A neural network is a computational model inspired by the structure of the human brain.")
    c.drawString(50, 620, "Deep learning is defined as a subset of machine learning based on artificial neural networks.")
    c.drawString(50, 600, "Neural networks learn by adjusting connection weights between artificial neurons.")
    c.showPage()
    
    # Page 2: Machine Learning Concepts
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 720, "Machine Learning Fundamentals")
    c.setFont("Helvetica", 11)
    c.drawString(50, 680, "Machine learning is a method of data analysis that automates analytical model building.")
    c.drawString(50, 660, "Supervised learning is an approach where models are trained on labeled training data.")
    c.drawString(50, 640, "Unsupervised learning refers to training models on unlabeled data to find hidden patterns.")
    c.drawString(50, 620, "Regression is a statistical method used to predict continuous outcomes.")
    c.drawString(50, 600, "Classification is defined as the process of predicting categorical labels for inputs.")
    c.showPage()
    
    # Page 3: Natural Language Processing
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 720, "Introduction to Natural Language Processing")
    c.setFont("Helvetica", 11)
    c.drawString(50, 680, "Natural language processing is a branch of artificial intelligence that helps computers understand human language.")
    c.drawString(50, 660, "Tokenization is a process where text is split into smaller units called tokens.")
    c.drawString(50, 640, "Stopword removal refers to removing common words like 'the' or 'is' to focus on important keywords.")
    c.drawString(50, 620, "Sentiment analysis is defined as the task of identifying the emotional tone behind a body of text.")
    c.drawString(50, 600, "Word embedding is a popular representation technique for mapping words to vector spaces.")
    c.showPage()
    
    c.save()
    print("Test PDF successfully created!")

if __name__ == "__main__":
    create_sample_pdf()
