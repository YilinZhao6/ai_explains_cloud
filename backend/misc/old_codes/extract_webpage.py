import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import html

def clean_math_formula(formula):
    """
    Clean and format math formula from Wikipedia's format to LaTeX-style markdown.
    """
    formula = formula.strip()
    formula = html.unescape(formula)
    formula = re.sub(r'\\displaystyle\s*', '', formula)
    return formula

def extract_content_html(url):
    """
    Extract main content from a URL and convert to HTML format.
    Preserves mathematical formulas using MathJax for rendering.
    
    Args:
        url (str): The URL to extract content from
        
    Returns:
        str: HTML formatted content with math formulas
    """
    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        html_content = []

        # Remove unwanted elements (headers, footers, navbars, etc.)
        for unwanted in soup.find_all(['header', 'footer', 'nav', 'aside', 'script', 'style']):
            unwanted.decompose()

        # Wikipedia-specific handling
        if 'wikipedia.org' in url:
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                html_content.extend(process_content(content_div))
        
        # Generic webpage handling
        else:
            main_content = extract_main_content(soup)
            if main_content:
                html_content.extend(process_content(main_content))
        
        # Add MathJax script for LaTeX rendering and join content
        mathjax_script = """
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML">
        </script>
        """
        final_content = mathjax_script + ''.join(html_content)
        
        return final_content

    except Exception as e:
        return f"Error extracting content: {str(e)}"

def extract_main_content(soup):
    """
    Try to find the main content of the webpage based on common content containers.
    
    Args:
        soup (bs4.BeautifulSoup): Parsed HTML soup object
        
    Returns:
        bs4.element.Tag: Main content tag if found, else None
    """
    # Common classes/IDs for main content containers
    main_selectors = [
        {'id': 'main-content'}, {'id': 'content'}, {'id': 'article-body'}, 
        {'class': 'post-content'}, {'class': 'entry-content'}, 
        {'class': 'main-article'}, {'class': 'article'}
    ]
    
    for selector in main_selectors:
        main_content = soup.find(attrs=selector)
        if main_content:
            return main_content
    
    # Fallback to the <body> tag if no specific container is found
    return soup.find('body')

def process_content(container):
    """
    Process HTML elements within the given container and convert to HTML format,
    preserving math formulas.
    
    Args:
        container (bs4.element.Tag): The container with content to process
        
    Returns:
        list: List of strings representing HTML content
    """
    content = []

    for element in container.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol']):
        content.extend(process_element(element))
    
    return content

def process_element(element):
    """
    Process individual HTML elements and convert to HTML format, preserving math formulas.
    
    Args:
        element (bs4.element.Tag): The HTML element to process
        
    Returns:
        list: List of strings representing HTML content
    """
    content = []

    if element.name == 'p':
        paragraph = element.get_text().strip()
        math_elements = element.find_all(['math', 'span', 'img'], 
                                         class_=['mwe-math-element', 'mwe-math-mathml-inline'])
        
        if math_elements:
            for math_elem in math_elements:
                latex = extract_latex(math_elem)
                if latex:
                    paragraph = paragraph.replace(math_elem.get_text(), f'<script type="math/tex">{latex}</script>')
        
        if paragraph:
            content.append(f"<p>{paragraph}</p>")

    elif element.name.startswith('h'):
        level = int(element.name[1])
        header_text = element.get_text().strip().replace('[edit]', '')
        content.append(f"<h{level}>{header_text}</h{level}>")
    
    elif element.name in ['ul', 'ol']:
        list_type = 'ul' if element.name == 'ul' else 'ol'
        content.append(f"<{list_type}>")
        for li in element.find_all('li', recursive=False):
            li_text = li.get_text().strip()
            math_elements = li.find_all(['math', 'span'], 
                                        class_=['mwe-math-element', 'mwe-math-mathml-inline'])
            if math_elements:
                for math_elem in math_elements:
                    latex = extract_latex(math_elem)
                    if latex:
                        li_text = li_text.replace(math_elem.get_text(), f'<script type="math/tex">{latex}</script>')
            content.append(f"<li>{li_text}</li>")
        content.append(f"</{list_type}>")
    
    return content

def extract_latex(math_elem):
    """
    Extract LaTeX content from a math element.
    
    Args:
        math_elem (bs4.element.Tag): The math-related HTML element
        
    Returns:
        str: LaTeX representation of the math element, if found
    """
    latex = None
    
    annotation = math_elem.find('annotation', {'encoding': 'application/x-tex'})
    if annotation:
        latex = clean_math_formula(annotation.string)
    
    elif math_elem.name == 'img' and math_elem.get('alt'):
        latex = clean_math_formula(math_elem.get('alt'))
    
    elif math_elem.name == 'math':
        latex = clean_math_formula(math_elem.get_text())
    
    return latex

def save_content_html(url):
    """
    Extract content from URL and save to HTML file.
    
    Args:
        url (str): The URL to extract content from
    """
    content = extract_content_html(url)
    
    filename = url.split('/')[-1].replace('_', '-').lower()
    if not filename.endswith('.html'):
        filename = f"{filename}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

# Example usage
if __name__ == "__main__":
    url = "https://www.britannica.com/science/moment-of-inertia"
    filename = save_content_html(url)
    print(f"Content saved to {filename}")
