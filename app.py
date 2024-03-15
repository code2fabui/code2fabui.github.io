from flask import Flask, request, send_from_directory, jsonify
import os
import subprocess
from openai import OpenAI  # Import OpenAI library

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", 'Insert you api key here')) 

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 3000))

@app.route('/generate-stl', methods=['POST'])
def generate_stl():
    code = request.json.get('code')
    try:
        result = subprocess.run(['openscad', '-o', './static/models/temp.stl', '-'], input=code, text=True, capture_output=True)
        if result.returncode != 0:
            print(f"exec error: {result.stderr}")
            return jsonify(error='Failed to generate STL file'), 500

        print(f"stdout: {result.stdout}")
        return jsonify(stlUrl='/static/models/temp.stl')

    except Exception as e:
        print(f"Execution error: {e}")
        return jsonify(error='Failed to generate STL file'), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/')
def call_gpt_api(text):
    command_template = \
    """
    Read the following report section carefully. 
    ***Report Begins***
    {text}
    ***Report Ends***
    Follow the template below to output the result:
    ***Template Begins***
    ##Summary of the section: ##
    [Insert the summary of the patient report here, highlighting key points and information.]

    ##Codes##
    "Code1", [Name of Code1], [Direct evidence from the supporting Code1]
    "Code2", [Name of Code2], [Direct evidence from the supporting Code2]
    ...
    ***Template Ends***

    """
    #print(command_template.format(whole_text=whole_text))
    try:
        # Generate completion from OpenAI's chat model
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            timeout=10,
            messages=[
                {"role": "system", "content": "You pay close attention to details and ensure that each code is supported by direct evidence from the report."},
                {"role": "user", "content": command_template.format(text=text)},
            ]
        )
        return completion.choices[0].message.content  # Return the predicted result
    except Exception as e:
        return "Error: " + str(e)
    
@app.route('/api/call-gpt', methods=['POST'])
def handle_gpt_request():
    data = request.json
    text = data['text']
    button_id = data['button_id']

    if button_id == 'describe':
        command_template = \
        """
    Prompt for describe 
    ***Report Begins***
    {text}
    ***Report Ends***
    Follow the template below to output the result:
    ***Template Begins***
    ##Summary of the section: ##
    [Insert the summary of the patient report here, highlighting key points and information.]

    ##Codes##
    "Code1", [Name of Code1], [Direct evidence from the supporting Code1]
    "Code2", [Name of Code2], [Direct evidence from the supporting Code2]
    ...
    ***Template Ends***

        """
    elif button_id == 'match':
        command_template = \
        """
    Prompt for match
    ***Report Begins***
    {text}
    ***Report Ends***
    Follow the template below to output the result:
    ***Template Begins***
    ##Summary of the section: ##
    [Insert the summary of the patient report here, highlighting key points and information.]

    ##Codes##
    "Code1", [Name of Code1], [Direct evidence from the supporting Code1]
    "Code2", [Name of Code2], [Direct evidence from the supporting Code2]
    ...
    ***Template Ends***

        """
    elif button_id == 'analysis':
        command_template = \
        """
    {text}
        """
    elif button_id == 'improve':
        command_template = \
        """
    Prompt for improve 
    ***Report Begins***
    {text}
    ***Report Ends***
    Follow the template below to output the result:
    ***Template Begins***
    ##Summary of the section: ##
    [Insert the summary of the patient report here, highlighting key points and information.]

    ##Codes##
    "Code1", [Name of Code1], [Direct evidence from the supporting Code1]
    "Code2", [Name of Code2], [Direct evidence from the supporting Code2]
    ...
    ***Template Ends***

        """
    else:
        return jsonify({'error': 'Invalid button identifier'}), 400

    response = call_gpt_api(text, command_template)
    return jsonify({'response': response})

def call_gpt_api(text, command_template):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            timeout=10,
            messages=[
                {"role": "system", "content": "hello"},
                {"role": "user", "content": command_template.format(text=text)},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Error: " + str(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

