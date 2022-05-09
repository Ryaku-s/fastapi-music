import uvicorn


def runserver(args):
    uvicorn.run('main:app', host=args.host, port=args.port, reload=args.reload)
