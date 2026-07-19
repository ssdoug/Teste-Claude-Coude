from workers import WorkerEntrypoint

from lib.router import route


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await route(request, self.env, self.ctx)
