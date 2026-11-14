FROM --platform=linux/amd64 debian:bookworm-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies needed to compile and run the challenge
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    gdb \
    xinetd \
    && rm -rf /var/lib/apt/lists/*

# Set up non-root user for challenge isolation
RUN useradd -m -s /bin/bash ctf

# Aggiungi cartelle user finte
RUN mkdir -p /home/john;     touch /home/john/CVE-2027-42069.exe
RUN mkdir -p /home/max;      touch /home/max/dont_waste_time.txt
RUN mkdir -p /home/alb4;     touch /home/alb4/wH3re_t0_f1nd_capyb4ras.json
RUN mkdir -p /home/alessaba; touch /home/alessaba/team_briscola_members.csv

WORKDIR /home/ctf

# Copy source code and flag into home directory
COPY speedrun.c /home/ctf/vuln.c
COPY flag.txt /home/ctf/flag.txt
COPY xinetd.conf /etc/xinetd.d/ctf
COPY ctf-run.sh /usr/local/bin/ctf-run

# Compile the vulnerable binary (adjust flags like -fno-stack-protector / -z execstack as needed)
RUN gcc -no-pie -Wl,-Ttext=0x570000 /home/ctf/vuln.c -o /home/ctf/vuln

# Set correct permissions
RUN chown -R root:root /home/ctf && \
    chmod 755 /home/ctf/vuln && \
    chmod 444 /home/ctf/flag.txt && \
    chmod 755 /usr/local/bin/ctf-run
    
RUN rm /home/ctf/vuln.c

EXPOSE 5295

CMD ["/usr/sbin/xinetd", "-dontfork"]
