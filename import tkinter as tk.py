import tkinter as tk
from tkinterweb import HtmlFrame

root = tk.Tk()
root.title("Shrink Bug Example")
root.geometry("300x180")


html_frame = HtmlFrame(master=root, javascript_enabled=True, javascript_backend="python")
def g():
    print(this)
html_frame.javascript.register("g", g)
html_frame.load_html("""

<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>JS Tester</title>
</head>
<body>
                     <script>
                     def hi():
                        this.value = "dsfsdf"
                     </script>
  <textarea id="code" rows="10" cols="60" onload="hi()">
  </textarea>
  <br><br>
  <button onclick="run()">Run</button>

  <pre id="out"></pre>

  <script>
    def run():
      output = []

      result = document.getElementById("code").value
      output.append(result)
      print(output)
      document.getElementById("out").textContent = "\\n".join(output)
  </script>
</body>
</html>
""")

html_frame.pack(pady=5)

root.mainloop()