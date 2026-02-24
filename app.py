import streamlit as st
from PIL import Image, ImageOps
import io
import base64

# High-Resolution A4 Canvas (300 DPI)
A4_WIDTH = 2480
A4_HEIGHT = 3508

def process_images(uploaded_files):
    images = []
    # Open images and correct any rotated photos from mobile devices
    for f in uploaded_files:
        img = Image.open(f)
        img = ImageOps.exif_transpose(img)
        images.append(img)
        
    num_images = len(images)
    pages = []
    
    # Process 8 images at a time (Max per page)
    chunk_size = 8
    for i in range(0, num_images, chunk_size):
        chunk = images[i:i + chunk_size]
        
        # Grid layout logic
        if len(chunk) == 1:
            cols, rows = 1, 1 
        elif len(chunk) <= 3:
            cols, rows = 2, 2 
        else:
            # 4 columns, 2 rows
            cols, rows = 4, 2 
            
        # Calculate maximum pixel size for each grid cell
        cell_width = A4_WIDTH // cols
        cell_height = A4_HEIGHT // rows
        
        # Create a blank white high-res A4 canvas
        canvas = Image.new('RGB', (A4_WIDTH, A4_HEIGHT), 'white')
        
        for idx, img in enumerate(chunk):
            col = idx % cols
            row = idx // cols
            
            # Resize image to fit cell (80px padding ensures they don't touch edges on print)
            img_resized = ImageOps.contain(img, (cell_width - 80, cell_height - 80), Image.Resampling.LANCZOS)
            
            # Calculate (x, y) to center the image perfectly in its cell
            x_offset = col * cell_width + (cell_width - img_resized.width) // 2
            y_offset = row * cell_height + (cell_height - img_resized.height) // 2
            
            # Paste the high-quality image onto the canvas
            canvas.paste(img_resized, (x_offset, y_offset))
            
        pages.append(canvas)
        
    return pages

# --- Streamlit UI ---
st.set_page_config(page_title="BNG-RIAA", layout="centered")

st.title("📄 BNG Reimbursement Ready")
st.write("Upload your photos to generate Reimbursement-Ready where you can print it directly")

uploaded_files = st.file_uploader("Upload Photos (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Generate & Prepare for Printing"):
        with st.spinner("Processing your high-res images..."):
            pages = process_images(uploaded_files)
            
            st.success(f"Successfully generated {len(pages)} high-quality page(s)!")
            
            # Convert to PDF
            pdf_bytes = io.BytesIO()
            pages[0].save(
                pdf_bytes, 
                format='PDF', 
                resolution=300.0, 
                save_all=True, 
                append_images=pages[1:]
            )
            
            # Display PDF directly in the app for instant printing
            st.subheader("🖨️ Ready to Print")
            st.write("Hover over the PDF below and click the **Printer icon** in the top right corner.")
            
            base64_pdf = base64.b64encode(pdf_bytes.getvalue()).decode('utf-8')
            # Embedding the PDF using an HTML iframe
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=1" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Keep the download button as a backup option
            st.download_button(
                label="📥 Or Download as PDF File",
                data=pdf_bytes.getvalue(),
                file_name="high_res_a4_photos.pdf",
                mime="application/pdf"
            )