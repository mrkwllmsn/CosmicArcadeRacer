# CosmicArcadeRacer
80s style arcade racer for Pimoroni Cosmic Unicorn, written in micropython.



## Try without installing on the pico...
You can either run it from your computer using thonny / mpremote

eg:
```shell
mpremote run ./cosmic_arcade_racer.py 
```

### Install it to the Pico:
You have already done a pip install mpremote? Cool. 

...copy it up with mpremote cp and call it main.py if you want it to always start when you turn the cosmic unicorn (CU) on.

eg:
```shell
mpremote cp ./cosmic_arcade_racer.py :main.py
```

then restart your CU, however you like. One way is this, or use a button on it.
```shell
mpremote reset
```


