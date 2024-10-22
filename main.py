from website import create_app

app = create_app()

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=8000, debug=True)
    #with hotspot to test on mobile
    app.run(debug=True)
    
