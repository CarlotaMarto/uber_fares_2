import os
import glob
import re

for page in glob.glob("pages/*.py"):
    with open(page, "r") as f:
        content = f.read()
    
    # Remove st.set_page_config calls
    content = re.sub(r'st\.set_page_config\([^)]*\)', '', content)
    
    # Remove inject_custom_css() calls
    content = re.sub(r'inject_custom_css\(\)', '', content)
    
    with open(page, "w") as f:
        f.write(content)
