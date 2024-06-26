FROM ims-base

COPY ./sampleData /sampleData

# Command to run the Flask application
CMD sh -c "python3 app.py"