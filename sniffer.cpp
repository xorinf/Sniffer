#include <arpa/inet.h>
#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <sys/socket.h>
#include <unistd.h>
#include <zmq.h> // You'll need to install libzmq

// Buffer size for capturing packets
#define BUFFER_SIZE 65536

int main() {
  // 1. Create a Raw Socket (Must run with sudo!)
  // AF_INET = IPv4, SOCK_RAW = Raw Socket, IPPROTO_TCP = Capture TCP packets
  // Note: On macOS, SOCK_RAW behavior can be restrictive.
  // We might need to adjust for macOS specifically if IPPROTO_TCP doesn't
  // capture everything expected, but we will stick to the user's provided code
  // for now.
  int raw_sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
  if (raw_sock < 0) {
    perror("Socket Error");
    return 1;
  }

  // 2. Setup ZeroMQ to talk to Python
  void *context = zmq_ctx_new();
  void *pusher = zmq_socket(context, ZMQ_PUSH);
  // Bind to a TCP port to push messages to the Python script
  int rc = zmq_bind(pusher, "tcp://*:5555");
  if (rc != 0) {
    perror("ZeroMQ Bind Error");
    return 1;
  }

  unsigned char *buffer = (unsigned char *)malloc(BUFFER_SIZE);

  printf("Sniffer started... Listening for packets.\n");

  while (true) {
    // 3. Receive Packet
    // recvfrom reads data from the socket
    int data_size = recvfrom(raw_sock, buffer, BUFFER_SIZE, 0, NULL, NULL);
    if (data_size < 0) {
      perror("Recv Error");
      return 1;
    }

    // 4. Extract IP Header
    // On macOS, use struct ip instead of struct iphdr
    struct ip *iph = (struct ip *)buffer;

    // Get Source IP as string
    struct in_addr ip_addr = iph->ip_src;
    char *src_ip = inet_ntoa(ip_addr);

    // 5. Create a simple string: "IP_ADDRESS,PACKET_SIZE"
    char message[100];
    snprintf(message, sizeof(message), "%s,%d", src_ip, data_size);

    // 6. Send to Python immediately
    // zmq_send sends the message to the connected PULL socket (in Python)
    zmq_send(pusher, message, strlen(message), 0);
    // printf("Sent: %s\n", message); // Debugging
  }

  close(raw_sock);
  free(buffer);
  zmq_close(pusher);
  zmq_ctx_destroy(context);
  return 0;
}
