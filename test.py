# app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
  return """
  <!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Lockbox</title>
	<link href="/static/assets/cubey.jpg" rel="stylesheet">
</head>
<body style="font-family: Open Sans, sans-serif;">
	<header>
		<h1>Lockbox</h1>
		<img src="/static/assets/cubey.jpg" id="logo" style="width: 100px">
	</header>
	<nav>
		<ul id="nav-list">
			<li><a href="#">Send</a></li>
			<li><a href="#">Receive</a></li>
        </ul>
	</nav>
	<main>
		<h2>Drop your files here to upload</h2>
		<div id="drop-file-here"></div>
	</main>
</body>
"""
