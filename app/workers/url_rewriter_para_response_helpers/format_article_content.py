import requests
import os
import uuid
import logging
import json
import time
import re
from app.workers.url_rewriter_para_request_helpers.content_processor import ContentProcessor
from app.workers.core.calculate_priority.calculate_priority import CalculatePriority
from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore
from app.config.config import AI_RATE_LIMITER_URL


class ArticleContentFormatter:
    def __init__(self):
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.content_handler = ContentProcessor()
        self.calculate_priority_service = CalculatePriority()
        self.ai_message_request_store_service = AIMessageRequestStore()
        

    # def format_article_content(self, content_data):
    #     try:
    #         # # Save original input
    #         # with open('demo_json/content_data.json', 'w', encoding='utf-8') as f:
    #         #     json.dump(content_data, f, ensure_ascii=False, indent=4)

    #         # Format and sort data
    #         formatted_output = []
    #         for item in content_data["data"]:
    #             try:
    #                 req = json.loads(item["ai_request"])
    #                 res = json.loads(item["ai_response"])
    #                 formatted_output.append({
    #                     "html_tag": req.get("html_tag", ""),
    #                     "sequence_index": req.get("sequence_index"),
    #                     "content": res.get("result", {}).get("processed_text"),
    #                     "article_id": req.get("article_id"),
    #                     "message_id": req.get("message_id"),
    #                 })
    #             except json.JSONDecodeError:
    #                 continue

    #         # Sort by sequence_index
    #         formatted_output.sort(key=lambda x: x["sequence_index"])

    #         # ✅ Dump directly as JSON object (not string)
    #         with open('demo_json/formated_content.json', 'w', encoding='utf-8') as f:
    #             json.dump(formatted_output, f, ensure_ascii=False, indent=4)            
            
            
    #         # Generate <body> content
    #         body_output = ['<body>']

    #         for item in formatted_output:
    #             tag = item["html_tag"]
    #             content = item["content"]

    #             # Convert markdown to HTML
    #             content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    #             content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)

    #             if tag == "title":
    #                 body_output.append(f"  <h1>{content}</h1>")
    #             elif tag == "paragraph":
    #                 body_output.append(f"  <p>{content}</p>")
    #             elif tag == "h2":
    #                 body_output.append(f"  <h2>{content}</h2>")
    #             elif tag == "ul":
    #                 body_output.append("  <ul>")
    #                 for line in content.strip().split('\n'):
    #                     if line.strip().startswith('-'):
    #                         li_content = line.strip()[1:].strip()
    #                         # Convert markdown in <li>
    #                         li_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', li_content)
    #                         li_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', li_content)
    #                         body_output.append(f"    <li>{li_content}</li>")
    #                 body_output.append("  </ul>")

    #         body_output.append('</body>')

    #         # Join as HTML string
    #         html_body = "\n".join(body_output)


    #         # ✅ Dump directly as JSON object (not string)
    #         with open('demo_json/html_body.html', 'w', encoding='utf-8') as f:
    #             f.write(html_body)

    #         # Optional: return the formatted output for use
    #         return {"success": True, "json_data": formatted_output, "html_data":html_body}

    #     except Exception as e:
    #         print(f"[format_article_content] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}




    def format_article_content(self, content_data):
        try:
            formatted_output = []
            for item in content_data["data"]:
                try:
                    req = json.loads(item["ai_request"])
                    res = json.loads(item["ai_response"])
                    formatted_output.append({
                        "html_tag": req.get("html_tag", ""),
                        "sequence_index": req.get("sequence_index"),
                        "content": res.get("result", {}).get("processed_text", ""),
                        "article_id": req.get("article_id"),
                        "message_id": req.get("message_id"),
                    })
                except json.JSONDecodeError:
                    continue

            # Sort by sequence_index
            formatted_output.sort(key=lambda x: x["sequence_index"])

            # Initialize parts
            body_output = ['<body>']
            generated_title = ""
            paragraph_contents = []

            for item in formatted_output:
                tag = item["html_tag"]
                content = item["content"]

                # Convert markdown to HTML
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)

                if tag == "title":
                    generated_title = content
                    body_output.append(f"  <h1>{content}</h1>")
                elif tag == "paragraph":
                    paragraph_contents.append(content)
                    body_output.append(f"  <p>{content}</p>")
                elif tag == "h2":
                    body_output.append(f"  <h2>{content}</h2>")
                elif tag == "ul":
                    body_output.append("  <ul>")
                    for line in content.strip().split('\n'):
                        if line.strip().startswith('-'):
                            li_content = line.strip()[1:].strip()
                            li_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', li_content)
                            li_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', li_content)
                            body_output.append(f"    <li>{li_content}</li>")
                    body_output.append("  </ul>")

            body_output.append('</body>')
            html_body = "\n".join(body_output)

            # ✅ Dump directly as JSON object (not string)
            with open('demo_json/final_html_body.html', 'w', encoding='utf-8') as f:
                f.write(html_body)

            return {
                "generated_title": generated_title,
                "generated_content": " ".join(paragraph_contents),
                "full_article": html_body
            }
            
            # return {
            #     "generated_title": "<h1><strong>Side Hustlers Season 2: Is It Happening? Renewal Status & What We Know So Far!</strong></h1>",
            #     "generated_content": """<em>(Because let’s be real—you’re not here for small talk. You want answers. And maybe some insider tea.)</em>  
            #             ### <strong>What Could <em>Side Hustlers Season 2</em> Look Like?</strong>  

            #             If (okay, <em>when</em>) Season 2 happens, here’s what we’re hoping for:  

            #             ✅ <strong>New Hustles, Same Chaos</strong> – More wild business ideas, more fails, more <em>"Why did they think this would work?"</em> gold.  
            #      """,
            #     "full_article": """<body>
            #             <h1><strong>Side Hustlers Season 2: Is It Happening? Renewal Status & What We Know So Far!</strong>  
            #             <em>(Because let’s be real—you’re not here for small talk. You want answers. And maybe some insider tea.)</em>  
            #     </body>"""
            # }

        except Exception as e:
            print(f"[format_article_content] Exception: {e}")
            return {
                "generated_title": "",
                "generated_content": "",
                "full_article": "",
                "error": f"Unexpected error: {str(e)}"
            }
