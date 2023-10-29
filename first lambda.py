import boto3
import os
from io import BytesIO
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

# Set your AWS access keys
AWS_ACCESS_KEY_ID = 'AKIA4RYGN3LPO2QAPAM6'
AWS_SECRET_ACCESS_KEY = 'CisKF6/Jd5uZYsfWVWlo7uusAyKUnvdwpJ8wR/eH'

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def process_pdf_from_s3(bucket_name, key_name, question):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key_name)
        raw_text = ''
       
        with BytesIO(response['Body'].read()) as f:
            pdf_reader = PdfReader(f)
            total_pages = len(pdf_reader.pages)

            for i, page in enumerate(pdf_reader.pages):
                content = page.extract_text()
                if content:
                    raw_text += content
                
            
        text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=800,
                chunk_overlap=200,
                length_function=len,
            )
        texts = text_splitter.split_text(raw_text)
                # Download embeddings from OpenAI
        embeddings = OpenAIEmbeddings()
        document_search = FAISS.from_texts(texts, embeddings)
        chain = load_qa_chain(OpenAI(), chain_type="stuff")
        docs = document_search.similarity_search(question)   
        x = chain.run(input_documents=docs, question=question)
        return x         

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

# Lambda handler function
def lambda_handler():
    try:
        # Extract necessary data from the S3 event
        # bucket_name = event['Records'][0]['s3']['bucket']['name']
        # key_name = event['Records'][0]['s3']['object']['key']
        bucket_name="chatpdf0409"
        key_name="Tata Capital RFP- Mortgage Legal Assistance.pdf"
        # Set your OpenAI API key
        os.environ["OPENAI_API_KEY"] = "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"


        # Call the function to process the PDF from S3
        result=process_pdf_from_s3(bucket_name, key_name, "give me the property details")

        print(result) 

        return {
            'statusCode': 200,
            'body': 'Processing complete'
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Error processing PDF'
        }

lambda_handler()


































# import boto3
# import os
# import tempfile
# from PyPDF2 import PdfReader
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.vectorstores import FAISS
# from langchain.chains.question_answering import load_qa_chain
# from langchain.llms import OpenAI

# # Set your AWS access keys
# AWS_ACCESS_KEY_ID = 'AKIA4RYGN3LPO2QAPAM6'
# AWS_SECRET_ACCESS_KEY = "CisKF6/Jd5uZYsfWVWlo7uusAyKUnvdwpJ8wR/eH"

# s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# def process_pdf_from_s3(bucket_name, key_name, question):
#     try:
#         temp_file = tempfile.NamedTemporaryFile(delete=False)

#         with open(temp_file.name, 'wb') as f:
#             s3.download_fileobj(bucket_name, key_name, f)

#         raw_text = ''
#         with open(temp_file.name, 'rb') as f:
#             pdf_reader = PdfReader(f)
#             total_pages = len(pdf_reader.pages)

#             for i, page in enumerate(pdf_reader.pages):
#                 content = page.extract_text()
#                 if content:
#                     raw_text += content
#             # print(raw_text)

#         text_splitter = CharacterTextSplitter(
#                 separator="\n",
#                 chunk_size=800,
#                 chunk_overlap=200,
#                 length_function=len,
#             )
#         texts = text_splitter.split_text(raw_text)
#                 # Download embeddings from OpenAI
#         embeddings = OpenAIEmbeddings()
#         document_search = FAISS.from_texts(texts, embeddings)
#         chain = load_qa_chain(OpenAI(), chain_type="stuff")
#         docs = document_search.similarity_search(question)   
#         x = chain.run(input_documents=docs, question=question)
#         return x         


#     except Exception as e:
#         print(f"Error processing PDF: {str(e)}")
#     finally:
#         os.unlink(temp_file.name)

# # Lambda handler function
# def lambda_handler():
#     try:
#         # Extract necessary data from the S3 event
#         # bucket_name = event['Records'][0]['s3']['bucket']['name']
#         # key_name = event['Records'][0]['s3']['object']['key']
#         bucket_name="chatpdf0409"
#         key_name="Tata Capital RFP- Mortgage Legal Assistance.pdf"

#         # Set your OpenAI API key
#         os.environ["OPENAI_API_KEY"] = "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"

#         # Call the function to process the PDF from S3
#         process_pdf_from_s3(bucket_name, key_name, "give me the property details?")

#         return {
#             'statusCode': 200,
#             'body': 'Processing complete'
#         }
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return {
#             'statusCode': 500,
#             'body': 'Error processing PDF'
#         }

# lambda_handler()