# Disappearing_Text_Writing_App
An online writing app where if you stop typing, your work will disappear.
To build an online writing app where the work disappears if the user stops typing, you can use Python along with a web framework like Flask and JavaScript to handle the client-side functionality. Here's a step-by-step guide to get you started:

1. Set up the project:
   - Install Flask by running `pip install flask` in your command prompt or terminal.
   - Create a new directory for your project.
   - Inside the project directory, create a virtual environment by running `python -m venv venv`.
   - Activate the virtual environment:
     - On Windows: `venv\Scripts\activate`
     - On macOS/Linux: `source venv/bin/activate`
   - Create a new file called `app.py` in your project directory.

2. Import the required modules:
   - Open `app.py` and add the following import statements:

   ```python
   from flask import Flask, render_template, request
   import os
   ```

3. Initialize the Flask application:
   - Add the following code to `app.py`:

   ```python
   app = Flask(__name__)
   app.config['SECRET_KEY'] = os.urandom(24)
   ```

4. Create routes for displaying the app and handling the text submission:
   - Add the following code to `app.py`:

   ```python
   @app.route('/')
   def index():
       return render_template('index.html')

   @app.route('/submit', methods=['POST'])
   def submit():
       text = request.form['text']
       if text:
           return text
       else:
           return 'empty'
   ```

5. Create the HTML template:
   - Create a new directory called `templates` inside your project directory.
   - Inside the `templates` directory, create a new file called `index.html`.
   - Add the following code to `index.html`:

   ```html
   <!DOCTYPE html>
   <html>
     <head>
       <title>Online Writing App</title>
       <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
       <script>
         var typingTimer;
         var doneTypingInterval = 2000;

         $(document).ready(function() {
           var textArea = $('#text');

           textArea.on('input', function() {
             clearTimeout(typingTimer);
             typingTimer = setTimeout(submitText, doneTypingInterval);
           });

           textArea.on('keydown', function() {
             clearTimeout(typingTimer);
           });
         });

         function submitText() {
           var text = $('#text').val();
           if (text.trim() === '') {
             $('#result').text('Your work has disappeared!');
           } else {
             $.post('/submit', { text: text }, function(response) {
               if (response === 'empty') {
                 $('#result').text('Your work has disappeared!');
               } else {
                 $('#result').text('Your work: ' + response);
               }
             });
           }
         }
       </script>
     </head>
     <body>
       <h1>Online Writing App</h1>
       <textarea id="text" rows="10" cols="50"></textarea>
       <div id="result"></div>
     </body>
   </html>
   ```

6. Run the application:
   - In your command prompt or terminal, navigate to your project directory.
   - Run `flask run` to start the Flask development server.
   - Open your web browser and visit `http://localhost:5000` to use the online writing app.

In this app, the JavaScript code captures the user's input in the textarea and waits for a specific interval of time (2