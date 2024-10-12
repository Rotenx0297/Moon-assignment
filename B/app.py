from flask import Flask, jsonify
import requests

app = Flask(__name__)

def get_metadata():
    """Fetch and return the EC2 instance metadata using a session token"""
    try:
        token_response = requests.put(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
            # Timeout to avoid hanging if the service is not available
            timeout=1  
        )
        token_response.raise_for_status()
        token = token_response.text
        # Fetch the metadata
        metadata_response = requests.get('http://169.254.169.254/latest/meta-data/', headers={'X-aws-ec2-metadata-token': token})
        metadata_response.raise_for_status()
        # Split the response into lines
        metadata = metadata_response.text.splitlines()  
        
        # Create a dictionary to hold the metadata
        metadata_dict = {}
        
        for item in metadata:
            # For each metadata item, fetch its value
            item_response = requests.get(f'http://169.254.169.254/latest/meta-data/{item}', headers={'X-aws-ec2-metadata-token': token})
            item_response.raise_for_status()
            metadata_dict[item] = item_response.text

        return metadata_dict
    # Handle exceptions
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

# Define a route to fetch and return the EC2 instance metadata
@app.route('/metadata', methods=['GET'])
def metadata():
    """Fetch and return the EC2 instance metadata"""
    metadata_dict = get_metadata()
    return jsonify(metadata_dict)

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=80)