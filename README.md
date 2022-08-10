# Coffee Shop Full Stack

This project involved creating a simple coffee shop application to demonstrate user authentication and authorization through Auth0. The application uses [Ionic](https://ionicframework.com/) as its frontend framework, supported by a [Flask](https://flask.palletsprojects.com/en/2.2.x/) backend.

Requirements of the application were as follows:

1. Display graphics representing the ratios of ingredients in each drink.
2. Allow **public users** to view drink names and graphics.
3. Allow the **shop baristas** to see the recipe information.
4. Allow the **shop managers** to create new drinks and edit existing drinks.

The focus of the project was on user authentication which means the actual functionality of the application has been kept barebones, with drink ingredients being represented by ratios of colours.

\<INSERT SCREENSHOT HERE\>

The project was completed as the final project for the Identity and Authentication module of [Udacity's Full Stack Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044).

## Getting Started

### Installing Dependencies

#### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

#### Frontend Dependencies

1. **Installing Node and NPM**
   This project depends on Nodejs and Node Package Manager (NPM). Before continuing, download and install Node from [https://nodejs.com/en/download](https://nodejs.org/en/download/)

2. **Installing Ionic Cli**
   The Ionic Command Line Interface is required to serve and build the frontend. Instructions for installing the CLI is in the [Ionic Framework Docs](https://ionicframework.com/docs/installation/cli).

3. **Installing project dependencies**
   This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run: `npm install`

#### Backend Dependencies

1. Developers are expected to have Python3 and pip installed
2. Create a new virtual environment `python3 -m venv venv` and activate: `source venv/bin/activate`
3. Install all dependencies: `pip install -r requirements.txt`

### Setting Up Auth0

#### Create Auth0 App, API and Roles

1. Create a [new Auth0 Account](https://auth0.com/signup)
2. Select a unique tenant domain
3. Create a [new, single page web application](https://auth0.com/docs/get-started/auth0-overview/create-applications)
4. Register a [new API](https://auth0.com/docs/get-started/auth0-overview/set-up-apis)
   - in API Settings:
     - Enable RBAC
     - Enable Add Permissions in the Access Token
5. Create [new API permissions](https://auth0.com/docs/manage-users/access-control/configure-core-rbac/manage-permissions):
   - `get:drinks`
   - `get:drinks-detail`
   - `post:drinks`
   - `patch:drinks`
   - `delete:drinks`
6. Create new roles for:
   - Barista
     - can `get:drinks-detail`
     - can `get:drinks`
   - Manager
     - can perform **all actions**
7. Create two new accounts and assign the accounts a role from above.

#### Configure Locally

Ionic uses a configuration file to manage environment variables. These variables ship with the transpiled software and should not include secrets.

- Open `frontend/src/environments/environments.ts` and set the variables listed.

### Running the Server

From the `backend/src` directory, run the following:

```bash
export FLASK_APP=api
export FLASK_ENV=development
flask run
```

The API stores data using a local [SQLite database](https://www.sqlite.org/index.html). This is automatically initialised when starting the server for the first time. Resetting the database is controlled by the [`db_drop_and_create_all`](https://github.com/m-c-hill/coffee-shop-api/blob/f8aac6736fbe38c8b89fd0aa5f3e8615be99fa39/backend/src/database/models.py#L23) function. To run this, simply uncomment [the following line in `src/api.py`](https://github.com/m-c-hill/coffee-shop-api/blob/main/backend/src/api.py#L15) and restart the server.

### Running the Frontend

[Ionic](https://ionicframework.com/) ships with a useful development server which detects changes and transpiles as you work. The application is then accessible through the browser on a localhost port. To run the development server, cd into the `frontend` directory and run:

```bash
ionic serve
```

## Theory

### Auth0

[Auth0](https://auth0.com/docs/get-started/auth0-overview) is a flexible, drop-in solution to add authentication and authorization services to applications. It minimises the cost, time, and risk associated with building an in-house solution to authenticate and authorize users.

![image](https://cdn.hashnode.com/res/hashnode/image/upload/v1616225393075/v2TJSq1Hb.png?auto=compress,format&format=webp)

The client requests authorization to the authorization server (performed by Auth0 in this case). Once the user has logged in and authorization is granted, the authorization server returns an access token to the application. The application uses the access token to access a protected resource (such as the restricted coffee API endpoints).

### Authentication

The authentication system used for this project is Auth0. `./src/app/services/auth.service.ts` contains the logic to direct a user to the Auth0 login page, managing the JWT token upon successful callback, and handle setting and retrieving the token from the local store. This token is then consumed by our DrinkService (`./src/app/services/drinks.service.ts`) and passed as an Authorization header when making requests to our backend.

### Authorization

The Auth0 JWT includes claims for permissions based on the user's role within the Auth0 system. This project makes use of these claims using the `auth.can(permission)` method which checks if particular permissions exist within the JWT permissions claim of the currently logged in user. This method is defined in `./src/app/services/auth.service.ts` and is then used to enable and disable buttons in `./src/app/pages/drink-menu/drink-form/drink-form.html`.

### JWT and Role-ased Access Control

[JWT (JSON Web Token)](https://jwt.io/introduction) is an open standard used to share security information between two parties — a client and a server.

JWT is a token based stateless authentication mechanism - the purpose is not to hide data but to ensure the authenticity of the data (it's signed and encoded, but rarely encrypted).

Each JWT contains encoded JSON objects, including a set of claims. JWTs are signed using a cryptographic algorithm to ensure that the claims cannot be altered after the token is issued.

Claims may include who issued the token, how long it is valid for and what permissions the client has been granted.

A JWT is a string composed of three sections, separated by dots and serialized using base64 (header.payload.signature).

When decoded, you get two JSON strings:

1. The header and the payload
2. The signature

![image](https://miro.medium.com/max/1400/1*u3a-5xZDeudKrFGcxHzLew.png)

#### Header

The header consists of token type and algorithm used for signing and encoding. Algorithms can be HMAC, SHA256, RSA, HS256 or RS256.

```
{
  "typ": "JWT",
  "alg": "RS256"
}
```

In our application, the algorithm used to sign the JWT is RS256 (RSA using SHA256). This is an asymmetric algorithm that uses a public/private key pair. The identity provider has a private key to generate the signature. The receiver of the JWT uses a public key to validate the JWT signature. The public key used to verify and the private key used to sign the token are linked since they are generated as a pair.

![image](https://aws1.discourse-cdn.com/auth0/original/3X/7/0/709aa9a1d6e7fb8944e525e956a34bb0d63554d7.png)

#### Payload

The payload contains the claims, displayed as a JSON string. Some standard claims include:

- issuer (iss)
- subject (sub)
- audience (aud)
- expiration time (exp)
- issued at (iat)

Custom claims can also be included. For example, these can be our API-specific permissions to allow users to access protected enpoints:

```
"permissions": [
    "delete:drinks",
    "get:drinks",
    "get:drinks-detail",
    "patch:drinks",
    "post:drinks"
  ]
```

#### Signature

The signature ensures that the token hasn’t been altered.

The party that creates the JWT signs the header and payload with a secret that is known to both the issuer and receiver, or with a private key known only to the sender. When the token is used, the receiving party verifies that the header and payload match the signature.

This ensures that if the JWT's payload is altered (ie. extra permissions are added), the signature needs to be calculated again.

## API Reference

- **Base URL**: Currently this application is only hosted locally. The backend is hosted at http://127.0.0.1:5000/
- **Authentication**: Requests must include a JWT Authorization token in the header of the form 'Bearer ${JWT token}'.

### Endpoints

**GET /drinks**

- Returns a complete list of drinks with limited information on their ingredients.
- Permissions required: none
- Example: `curl http://127.0.0.1:5000/drinks`

```
{
    "drinks": [
        {
            "id": 1,
            "recipe": [
                {
                    "color": "blue",
                    "parts": 1
                }
            ],
            "title": "water"
        },
        {
            "id": 2,
            "recipe": [
                {
                    "color": "grey",
                    "parts": 1
                },
                {
                    "color": "green",
                    "parts": 3
                }
            ],
            "title": "matchashake"
        }
    ],
    "success": true
}
```

**GET /drinks-detail**

- Returns a complete list of drinks with full information on their ingredients.
- Permissions required: get:drinks-detail
- Example: `curl http://127.0.0.1:5000/drinks-detail`

```
{
    "drinks": [
        {
            "id": 1,
            "recipe": [
                {
                    "color": "blue",
                    "name": "water",
                    "parts": 1
                }
            ],
            "title": "water"
        },
        {
            "id": 2,
            "recipe": [
                {
                    "color": "grey",
                    "name": "milk",
                    "parts": 1
                },
                {
                    "color": "green",
                    "name": "matcha",
                    "parts": 3
                }
            ],
            "title": "matchashake"
        }
    ],
    "success": true
}
```

**POST /drinks**

- Create a new drink with details provided by post request body.
- Permissions required: post:drinks
- Example: `curl http://127.0.0.1:5000/drinks/2 -X POST -H "Content-Type: application/json" -d '{"title": "chocolate milkshake", "recipe": [{color: "brown", name: "chocolate", parts: 2}, {color: "white", name: "milk", parts: 5}]}'`

```
{
    "drinks": [
        {
            "id": 5,
            "recipe": [
                {
                    "color": "brown",
                    "name": "chocolate",
                    "parts": 5
                },
                {
                    "color": "white",
                    "name": "milk",
                    "parts": 2
                }
            ],
            "title": "chococlate milkshake"
        }
    ],
    "success": true
}
```

**PATCH /drinks/${drink_id}**

- Update information for a specific drink using information provided by the post request body.
- Permissions required: patch:drinks
- Example: `curl http://127.0.0.1:5000/drinks/2 -X POST -H "Content-Type: application/json" -d '{"recipe": [{color: "grey", name: "milk", parts: 1}, {color: "green", name: "matcha", parts: 3}]}'`

```
{
    "drinks": [
        {
            "id": 2,
            "recipe": [
                {
                    "color": "grey",
                    "name": "milk",
                    "parts": 1
                },
                {
                    "color": "green",
                    "name": "matcha",
                    "parts": 3
                }
            ],
            "title": "matchashake"
        }
    ],
    "success": true
}
```

**DELETE /drinks/${drink_id}**

- Remove a drink from the menu.
- Permissions required: delete: drink
- `curl http://127.0.0.1:5000/drinks/3 -X DELETE`

```
{
    "delete": 3,
    "success": true
}
```

### Error Handling

Errors are returned as JSON in the following format:

```
{
    "success": False,
    "error": 404,
    "message": "resource not found"
}
```

The API returns three types of errors:

- 400 – bad request
- 401 - unauthorized
- 404 – resource not found
- 422 – unprocessable
