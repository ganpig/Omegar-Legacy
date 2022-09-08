from app import App

if __name__ == '__main__':
    app = App()
    while True:
        app.draw()
        app.process_events()
