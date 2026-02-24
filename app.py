import streamlit as st
from PIL import Image, ImageOps
import io

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
            
            # Resize image to fit cell with LANCZOS for high quality
            img_resized = ImageOps.contain(img, (cell_width - 80, cell_height - 80), Image.Resampling.LANCZOS)
            
            # Calculate (x, y) to center the image perfectly in its cell
            x_offset = col * cell_width + (cell_width - img_resized.width) // 2
            y_offset = row * cell_height + (cell_height - img_resized.height) // 2
            
            # Paste the high-quality image onto the canvas
            canvas.paste(img_resized, (x_offset, y_offset))
            
        # Explicitly tag the canvas with 300 DPI metadata
        canvas.info['dpi'] = (300, 300)
        pages.append(canvas)
        
    return pages

# --- Streamlit UI ---
st.set_page_config(page_title="BNG-RRG", layout="centered")

st.title("📄BNG Reimbursement-Ready")
st.write("Upload the photos to generate a perfectly 4x4 grid, ready for printing and reimbursement submission.")

uploaded_files = st.file_uploader("Upload Photos (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Generate High-Quality PDF"):
        with st.spinner("Processing your high-res images. This might take a moment..."):
            pages = process_images(uploaded_files)
            
            st.success(f"Successfully generated {len(pages)} high-quality page(s)!")
            
            # --- SCROLLABLE PREVIEW SECTION ---
            st.subheader("Preview:")
            
            # This creates a box 600 pixels high. If the images take up more space, 
            # Streamlit automatically adds a vertical scrollbar!
            with st.container(height=600):
                for idx, page in enumerate(pages):
                    st.image(page, caption=f"Page {idx + 1}", use_container_width=True)
            
            st.write("---")
                
            # Convert to PDF
            pdf_bytes = io.BytesIO()
            pages[0].save(
                pdf_bytes, 
                format='PDF', 
                resolution=300.0, 
                save_all=True, 
                append_images=pages[1:]
            )
            pdf_bytes.seek(0)
            
            # st.info("💡 **Printing Tip:** Once downloaded, open this PDF in Chrome, Edge, or Adobe Acrobat to print. Avoid opening it in Microsoft Word.")
            
            # Safe download button
            st.download_button(
                label="📥 Download Ready-to-Print PDF",
                data=pdf_bytes,
                file_name="high_res_a4_photos.pdf",
                mime="application/pdf"
            )