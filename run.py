# Load environment variables
import argparse
from projects import app

# Handling arguments
parser = argparse.ArgumentParser(description='Start the projects website')
parser.add_argument('--debug', dest='debug', action='store_true',
                    default=False,
                    help='Whether the application should run in debug mode')
parser.add_argument('--port', dest='port', type=int, default=80,
                    help='The port the webserver should listen on')
args = parser.parse_args()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
