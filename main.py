import os
from invoice_pipeline import InvoicePipeline

def main():
    pdf_path = "ali.pdf"  # path to your invoice PDF
    

    pipeline = InvoicePipeline()
    result = pipeline.process(pdf_path, preprocess=True)

    print("✅ Processing Summary:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
