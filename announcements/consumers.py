from channels.generic.websocket import AsyncConsumer
import json
import re

class CounterConsumer(AsyncConsumer):
    android_clients = set()
    ios_clients = set()
    desktop_clients = set()

    async def websocket_connect(self, event):
        self.token = await self.get_valid_token()
        self.device_type = self.get_device_type()
        self.client_id = tuple(self.scope['client'])

        await self.send({
            "type": "websocket.accept"
        })

        if self.token:
            # Admin connection
            self.admin_group_name = 'admin'
            await self.channel_layer.group_add(
                self.admin_group_name,
                self.channel_name
            )
            await self.send_current_client_info_to_admin()
        else:
            # Client connection
            await self.channel_layer.group_add(
                'clients',
                self.channel_name
            )
            self.add_client()
            await self.channel_layer.group_send(
                'admin',
                {
                    'type': 'client.connect',
                    'device_type': self.device_type,
                    'client_id': self.client_id
                }
            )

    async def websocket_disconnect(self, event):
        if self.token:
            # Admin disconnection
            await self.channel_layer.group_discard(
                self.admin_group_name,
                self.channel_name
            )
        else:
            # Client disconnection
            self.remove_client()
            await self.channel_layer.group_discard(
                'clients',
                self.channel_name
            )
            await self.channel_layer.group_send(
                'admin',
                {
                    'type': 'client.disconnect',
                    'device_type': self.device_type,
                    'client_id': self.client_id
                }
            )

    async def websocket_receive(self, event):
        # Handle any data received
        pass

    async def client_connect(self, event):
        await self.send_current_client_info_to_admin()

    async def client_disconnect(self, event):
        await self.send_current_client_info_to_admin()

    async def send_current_client_info_to_admin(self):
        client_count = await self.get_client_count()
        await self.channel_layer.group_send(
            'admin',
            {
                'type': 'admin.message',
                'message': client_count,
            }
        )

    async def admin_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": json.dumps({
                'message': event['message']
            })
        })

    async def get_client_count(self):
        return {
            'android': len(self.android_clients),
            'ios': len(self.ios_clients),
            'desktop': len(self.desktop_clients)
        }

    async def get_valid_token(self):
        token = self.scope['url_route']['kwargs'].get('token', None)
        return token if token and len(token) > 10 else None

    def get_device_type(self):
        user_agent = self.get_user_agent()
        if re.search(r'iPhone|iPad|iPod', user_agent):
            return 'iOS'
        elif re.search(r'Android', user_agent):
            return 'Android'
        elif re.search(r'Windows|Macintosh|Linux', user_agent):
            return 'Desktop'
        else:
            return 'Other'

    def get_user_agent(self):
        headers = dict(self.scope['headers'])
        user_agent = headers.get(b'user-agent', b'').decode('utf-8')
        return user_agent

    def add_client(self):
        if self.device_type == 'Android':
            self.android_clients.add(self.client_id)
        elif self.device_type == 'iOS':
            self.ios_clients.add(self.client_id)
        elif self.device_type == 'Desktop':
            self.desktop_clients.add(self.client_id)

    def remove_client(self):
        if self.device_type == 'Android':
            self.android_clients.discard(self.client_id)
        elif self.device_type == 'iOS':
            self.ios_clients.discard(self.client_id)
        elif self.device_type == 'Desktop':
            self.desktop_clients.discard(self.client_id)
