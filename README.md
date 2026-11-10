\# UM-Campus-Core-Net: Week 2 assignment



A network described as data (`topology.yaml`), checked, built in Mininet and

documented as a web page generated from the same file.



Published page: https://yanping-teow.github.io/netlab-week2/



\## Files

\- `topology.yaml` / `topology.json`: the network as data (3 switches, 6 hosts,

&#x20; dual-stack IPv4/IPv6 from my own address blocks)

\- `build\_topo.py`: checks the data with `check()`, then builds the network

\- `bad.yaml`: a deliberately broken copy used to prove `check()` works

\- `make\_page.py` and `page.yaml`: generate `docs/index.html` and hold my answers

\- `evidence/`: output from the running network (pingall, neighbour table,

&#x20; switch MAC table, duplicate-address test, check output)

\- `docs/`: the generated page, published with GitHub Pages



\## How to run

Inside the course container (`firdaussahran/netlab-mininet:1.0`):



&#x20;   python3 build\_topo.py topology.yaml

&#x20;   python3 build\_topo.py bad.yaml        # stops with PROBLEM lines

&#x20;   python3 make\_page.py topology.yaml    # writes docs/index.html



\## AI use

Tool: Claude (Anthropic).

What it did: explained the assignment; helped me find and fix address mistakes

in my topology; suggested making the network a tree to avoid a loop; drafted the

duplicate-address and bad-link logic in `check()`, the `links\_section()` and

`mermaid\_diagram()` functions, the evidence section of `make\_page.py`, and the

three written answers in `page.yaml`; and helped me debug Windows, Docker and

Git commands.

What I did myself: designed the network, built and ran it in Mininet, collected

the evidence, reviewed and edited the code and answers, and committed the work.

I tested all of it and can explain it.

