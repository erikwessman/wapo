FROM python:3.10
WORKDIR /usr/src/app
COPY . .

# Update packages, install zsh and git
RUN apt-get update && apt-get install -y zsh git && apt-get clean

# Install oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt
