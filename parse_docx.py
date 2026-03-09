import mammoth

# 解析 DOCX 文件
def parse_docx(file_path):
    try:
        with open(file_path, 'rb') as file:
            result = mammoth.convert_to_html(file)
            html = result.value
            print("=== DOCX 文件内容 ===")
            print(html)
            print("\n=== 解析完成 ===")
    except Exception as e:
        print(f"解析错误: {e}")

if __name__ == "__main__":
    file_path = "智能起重机维保系统_PRD完整版.docx"
    parse_docx(file_path)