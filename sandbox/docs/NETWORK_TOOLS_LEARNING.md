# Networking Tools & Concepts

## 1. Traceroute

### What it does
`traceroute` (or `tracert` on Windows) maps the exact path that data packets take across the internet from your computer to a destination server.

**Key features:**
- **Hops:** Displays every router or gateway the data bounces through.
- **Latency:** Measures the time (in milliseconds) taken to reach each hop.
- **Diagnostic Power:** Identifies exactly where a connection slows down or drops (e.g., at your ISP or the destination's network firewall).

### How to use it
Run the command in your terminal followed by a domain or IP address:
```bash
traceroute google.com
```
*(Note: Seeing asterisks `* * *` is normal; it indicates a router is configured to drop ping requests for security).*

---

## 2. Using Your Domain (`sketchmyinfra.com`) for Diagnostics
You can use standard networking tools against your own domain to verify infrastructure health:
- **Routing Verification:** `traceroute sketchmyinfra.com` confirms the physical routing path and verifies if DNS is resolving to the correct underlying server.
- **CDN/Proxy Validation:** It helps confirm if your traffic is successfully hitting your Cloudflare Edge network or AWS Load Balancer before reaching the origin server.
- **Latency Testing:** Allows you to measure physical network delays between your users and your hosting environment.

---

## 3. Wireshark

### What it does
While `traceroute` maps the path of data, **Wireshark** is a Network Protocol Analyzer (packet sniffer) that looks *inside* the data itself.

**Primary Use Cases:**
- **Deep Packet Inspection:** Viewing raw HTTP headers, API payloads, or database queries flowing through your network interface.
- **Security Analysis:** Detecting plain-text credential leaks, strange port activity, or analyzing malicious traffic.
- **Low-Level Debugging:** Inspecting TCP handshakes and ensuring TLS/SSL connections are negotiating properly.
