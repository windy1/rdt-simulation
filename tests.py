import unittest
from threading import Thread

from rdt import rdt


class TestRdt(unittest.TestCase):

    string = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam feugiat orci vehicula nunc efficitur, et 
    consequat elit eleifend. Phasellus molestie non nisi at tristique. Vivamus eu porta nunc. Donec sapien dui, 
    dictum ut facilisis id, euismod sed eros. Morbi et turpis ac dolor viverra hendrerit. Maecenas quis hendrerit 
    ex, ac rhoncus metus. Cras magna lectus, ornare sed porta eget, scelerisque at sem. Aenean eget dignissim ex. 
    Proin sollicitudin enim in risus tristique bibendum. In hac habitasse platea dictumst. Suspendisse tincidunt 
    nisl vel orci finibus, at posuere purus luctus. Maecenas auctor, urna at venenatis ultricies, urna erat 
    vulputate urna, semper efficitur enim purus vitae nisl. Etiam maximus ex velit, vel lacinia enim lacinia non.
    """

    def test_send_all(self):
        recv_thread = Thread(target=self.start_receiver)
        recv_thread.start()
        client = rdt(
            packet_loss=0,
            reorder=0,
            seg_size=16,
            wind=10,
            src_addr=('127.0.0.1', 8001),
            dest_addr=('127.0.0.1', 8000)
        )
        client.send_all(self.string)

    def start_receiver(self):
        server = rdt(
            packet_loss=0,
            reorder=0,
            seg_size=16,
            wind=10,
            src_addr=('127.0.0.1', 8000),
            server=True
        )
        result = server.recv_all()
        self.assertEqual(result, self.string)
        print(result)


if __name__ == "__main__":
    unittest.main()
