from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import numpy
nltk.download('punkt')

def summarize(text, language="english", sentences_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return ' '.join([str(sentence) for sentence in summary])

if __name__ == "__main__":
    text = "Moonlighting proteins are multifunctional, singlepolypeptide chains capable of performing multiple autonomous functions. Most moonlighting proteins have been discovered through work unrelated to their multifunctionality. We believe that prediction of moonlighting proteins from first principles, that is, using sequence, predicted structure, evolutionary profiles, and global gene expression profiles, for only one functional class of proteins in a single organism at a time will significantly advance our understanding of multifunctional proteins. In this work, we investigated human moonlighting DNA-binding proteins (mDBPs) in terms of properties that distinguish them from other (non-moonlighting) proteins with the same DNA-binding protein (DBP) function. Following a careful and comprehensive analysis of discriminatory features, a machine learning model was developed to assess the predictability of mDBPs from other DBPs (oDBPs). We observed that mDBPs can be discriminated from oDBPs with high accuracy of 74% AUC of ROC using these first principles features. A number of novel predicted mDBPs were found to have literature support for their being moonlighting and others are proposed as candidates, for which the moonlighting function is currently unknown. We believe that this work will help in deciphering and annotating novel moonlighting DBPs and scale up other functions. The source codes and data sets used for this work are freely available at https://zenodo.org/record/7299265#.Y2pO3ctBxPY"
    summary = summarize(text)
    print(summary)