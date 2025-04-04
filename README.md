## Bitwarden Configuration
BITWARDEN_ACCESS_TOKEN=0.8c2a418d-5d62-4a91-a530-b2a600ae957b.uLBNwqoBzm6CetMeP9MEvM0oUUqCGQ:s9Rycp0+uecneTWiPsmhLw==

# Base64-encoded Secret IDs
SECRET_ID_USERNAME=OTI5MTlhN2YtYTc2ZC00NGJiLTk0MWMtYjJhNTAwZjhmYjgz
SECRET_ID_PASSWORD=ZWYzY2FmMmItMjFjNS00MDM4LTg1ZDMtYjJiMzAwZTUyYTYw

# python-scripts

# Installing Required Packages for Python 2.7 (Deprecated)

Since Python 2.7 is deprecated, it's essential to pin specific versions of libraries that support it. Follow the steps below to install the necessary packages:

## Step 1: Install Required Packages

Run the following command to install the required dependencies:

```
pip install \
  requests==2.23.0 \
  urllib3==1.26.6 \
  certifi==2020.12.5 \
  idna==2.10 \
  chardet==3.0.4 \
  pyOpenSSL==19.1.0 \
  ndg-httpsclient==0.5.1 \
  pyasn1==0.4.8


# AT&T Residential Gateway (RG) Image Detection Use Cases

This repository includes a set of AI-assisted tasks for detecting and verifying the status of AT&T Residential Gateways (RG) in images. Below are the key use cases that our model addresses:

## Use Case 1: Verifying the image is of the correct object (AT&T RG)

### System Prompt:
You are an AI assistant trained to identify AT&T Residential Gateways (RG) in images. The image provided should be checked to ensure it does not contain objects like faces of dogs, cats, or unrelated items. If the object is an AT&T RG, confirm that it is correctly detected.

### User Prompt:
> Is this image of an AT&T Residential Gateway, or does it contain something unexpected (e.g., a dog or a cat)?

---

## Use Case 2: Identifying the angle (front/side/back) of the RG

### System Prompt:
You are an AI assistant trained to detect the angle of a device in an image. The object in the image must be an AT&T Residential Gateway (RG). Determine whether the image is showing the front, side, or back of the RG.

### User Prompt:
> Is this image showing the front, side, or back of the AT&T Residential Gateway?

---

## Use Case 3: Checking the lights status (ON/OFF) in the image

### System Prompt:
You are an AI assistant trained to detect the status of lights on an AT&T Residential Gateway (RG) from images. The lights should be identified as ON or OFF based on the visual data. If possible, identify which specific lights are ON.

### User Prompt:
> Which lights are ON in this image of the AT&T Residential Gateway? Are any lights OFF?
---
## Use Case 4: Identifying both the view and light status of the RG

### System Prompt:
You are an AI assistant trained to identify the AT&T Residential Gateway (RG) and analyze its status in an image. You should detect both the angle of the RG (whether it is showing the front, side, or back) and the status of the lights (ON or OFF) visible on the RG. If any specific light is ON, please mention which one, and if any light is OFF, state that as well.

### User Prompt:
> Can you tell me the angle (front, side, or back) of the AT&T Residential Gateway in this image and which lights are ON or OFF?

---


messages = [
    {
        "role": "system",
        "content": (
            "You are an AI assistant specialized in analyzing residential gateway devices. "
            "Analyze the images and identify all ports with connected cables. For each connected cable, provide "
            "the port location, cable color, and insertion status. If no cables are detected, report that no cables are plugged in."
        )
    },
    {
        "role": "user",
        "content": images_base64 + [
            {
                "type": "text",
                "text": "Identify the ports with cables plugged in, their colors, and insertion statuses. "
                        "If no cables are plugged in, provide a meaningful response indicating that."
            }
        ]
    }
]



