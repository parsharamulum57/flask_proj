import cohere
from flask import Flask, send_file, request, jsonify
#from graphviz import Digraph
#from PIL import Image
import os
import io
import zipfile
from openai import OpenAI


app = Flask(__name__)
prompt='''generate Entity Relationship Model in the following format :
entities = {
    'entity1': ['id', ....],
     'entity2': ['id', ....],
}
relationships = [
    ('entity1', 'entity2', 'many_to_many'),
    ('entity2', 'entity1', 'one_to_many')
]
where entity1, entity2 are examples names to give you as an example. Please change them accordingly and give the reponse json format. 

from swagger yaml given below:

{

swagger: "2.0"
info:
  description: "This is a sample server Petstore server.  You can find out more about Swagger at <a href=\"http://swagger.io\">http://swagger.io</a> or on irc.freenode.net, #swagger.  For this sample, you can use the api key \"special-key\" to test the authorization filters"
  version: 1.0.0
  title: Swagger Petstore YAML
  termsOfService: "http://swagger.io/terms/"
  contact:
    email: "apiteam@swagger.io"
  license:
    name: Apache 2.0
    url: "http://www.apache.org/licenses/LICENSE-2.0.html"
basePath: /v2
tags:
  - name: pet
    description: Everything about your Pets
    externalDocs:
      description: Find out more
      url: "http://swagger.io"
  - name: store
    description: Operations about user
  - name: user
    description: Access to Petstore orders
    externalDocs:
      description: Find out more about our store
      url: "http://swagger.io"
schemes:
  - http
paths:
  /pet:
    post:
      tags:
        - pet
      summary: Add a new pet to the store
      x-swagger-router-controller: SampleController
      description: ""
      operationId: addPet
      consumes:
        - application/json
        - application/xml
      produces:
        - application/xml
        - application/json
      parameters:
        - in: body
          name: body
          description: Pet object that needs to be added to the store
          required: false
          schema:
            $ref: "#/definitions/Pet"
      responses:
        "405":
          description: Invalid input
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
    put:
      tags:
        - pet
      summary: Update an existing pet
      description: ""
      operationId: updatePet
      consumes:
        - application/json
        - application/xml
      produces:
        - application/xml
        - application/json
      parameters:
        - in: body
          name: body
          description: Pet object that needs to be added to the store
          required: false
          schema:
            $ref: "#/definitions/Pet"
      responses:
        "400":
          description: Invalid ID supplied
        "404":
          description: Pet not found
        "405":
          description: Validation exception
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
  /pet/findByStatus:
    get:
      tags:
        - pet
      summary: Finds Pets by status
      description: Multiple status values can be provided with comma separated strings
      operationId: findPetsByStatus
      consumes:
        - application/xml
        - application/json
        - multipart/form-data
        - application/x-www-form-urlencoded
      produces:
        - application/xml
        - application/json
      parameters:
        - name: status
          in: query
          description: Status values that need to be considered for filter
          required: false
          type: array
          items:
            type: string
          collectionFormat: multi
          default: available
          enum:
            - available
            - pending
            - sold
      responses:
        "200":
          description: successful operation
          schema:
            type: array
            items:
              $ref: "#/definitions/Pet"
        "400":
          description: Invalid status value
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
  /pet/findByTags:
    get:
      tags:
        - pet
      summary: Finds Pets by tags
      description: "Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing."
      operationId: findPetsByTags
      produces:
        - application/xml
        - application/json
      parameters:
        - name: tags
          in: query
          description: Tags to filter by
          required: false
          type: array
          items:
            type: string
          collectionFormat: multi
      responses:
        "200":
          description: successful operation
          schema:
            type: array
            items:
              $ref: "#/definitions/Pet"
        "400":
          description: Invalid tag value
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
  "/pet/{petId}":
    get:
      tags:
        - pet
      summary: Find pet by ID
      description: Returns a single pet
      operationId: getPetById
      consumes:
        - application/x-www-form-urlencoded
      produces:
        - application/xml
        - application/json
      parameters:
        - name: petId
          in: path
          description: ID of pet to return
          required: true
          type: integer
          format: int64
      responses:
        "200":
          description: successful operation
          schema:
            $ref: "#/definitions/Pet"
        "400":
          description: Invalid ID supplied
        "404":
          description: Pet not found
      security:
        - api_key: []
        - petstore_auth:
            - "write:pets"
            - "read:pets"
    post:
      tags:
        - pet
      summary: Updates a pet in the store with form data
      description: ""
      operationId: updatePetWithForm
      consumes:
        - application/x-www-form-urlencoded
      produces:
        - application/xml
        - application/json
      parameters:
        - name: petId
          in: path
          description: ID of pet that needs to be updated
          required: true
          type: string
        - name: name
          in: formData
          description: Updated name of the pet
          required: false
          type: string
        - name: status
          in: formData
          description: Updated status of the pet
          required: false
          type: string
      responses:
        "405":
          description: Invalid input
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
    delete:
      tags:
        - pet
      summary: Deletes a pet
      description: ""
      operationId: deletePet
      consumes:
        - multipart/form-data
        - application/x-www-form-urlencoded
      produces:
        - application/xml
        - application/json
      parameters:
        - name: api_key
          in: header
          description: ""
          required: false
          type: string
        - name: petId
          in: path
          description: Pet id to delete
          required: true
          type: integer
          format: int64
      responses:
        "400":
          description: Invalid pet value
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
  "/pet/{petId}/uploadImage":
    post:
      tags:
        - pet
      summary: uploads an image
      x-swagger-router-controller: SampleController
      description: ""
      operationId: uploadFile
      consumes:
        - multipart/form-data
      produces:
        - application/json
      parameters:
        - name: petId
          in: path
          description: ID of pet to update
          required: true
          type: integer
          format: int64
        - name: additionalMetadata
          in: formData
          description: Additional data to pass to server
          required: false
          type: string
        - name: file
          in: formData
          description: file to upload
          required: false
          type: file
      responses:
        "200":
          description: successful operation
          schema:
            $ref: "#/definitions/ApiResponse"
      security:
        - petstore_auth:
            - "write:pets"
            - "read:pets"
  /store/inventory:
    get:
      tags:
        - store
      summary: Returns pet inventories by status
      description: Returns a map of status codes to quantities
      operationId: getInventory
      produces:
        - application/json
      parameters: []
      responses:
        "200":
          description: successful operation
          schema:
            type: object
            additionalProperties:
              type: integer
              format: int32
      security:
        - api_key: []
  /store/order:
    post:
      tags:
        - store
      summary: Place an order for a pet
      description: ""
      operationId: placeOrder
      produces:
        - application/xml
        - application/json
      parameters:
        - in: body
          name: body
          description: order placed for purchasing the pet
          required: false
          schema:
            $ref: "#/definitions/Order"
      responses:
        "200":
          description: successful operation
          schema:
            $ref: "#/definitions/Order"
        "400":
          description: Invalid Order
  "/store/order/{orderId}":
    get:
      tags:
        - store
      summary: Find purchase order by ID
      description: "For valid response try integer IDs with value <= 5 or > 10. Other values will generated exceptions"
      operationId: getOrderById
      produces:
        - application/xml
        - application/json
      parameters:
        - name: orderId
          in: path
          description: ID of pet that needs to be fetched
          required: true
          type: string
      responses:
        "200":
          description: successful operation
          schema:
            $ref: "#/definitions/Order"
        "400":
          description: Invalid ID supplied
        "404":
          description: Order not found
    delete:
      tags:
        - store
      summary: Delete purchase order by ID
      description: For valid response try integer IDs with value < 1000. Anything above 1000 or nonintegers will generate API errors
      operationId: deleteOrder
      produces:
        - application/xml
        - application/json
      parameters:
        - name: orderId
          in: path
          description: ID of the order that needs to be deleted
          required: true
          type: string
      responses:
        "400":
          description: Invalid ID supplied
        "404":
          description: Order not found
  /user:
    post:
      tags:
        - user
      summary: Create user
      description: This can only be done by the logged in user.
      operationId: createUser
      produces:
        - application/xml
        - application/json
      parameters:
        - in: body
          name: body
          description: Created user object
          required: false
          schema:
            $ref: "#/definitions/User"
      responses:
        default:
          description: successful operation
  /user/createWithArray:
    post:
      tags:
        - user
      summary: Creates list of users with given input array
      description: ""
      operationId: createUsersWithArrayInput
      produces:
        - application/xml
        - application/json
      parameters:
        - in: body
          name: body
          description: List of user object
          required: false
          schema:
            type: array
            items:
              $ref: "#/definitions/User"
      responses:
        default:
          description: successful operation
  /user/createWithList:
    post:
      tags:
        - user
      summary: Creates list of users with given input array
      description: ""
      operationId: createUsersWithListInput
      produces:
        - application/xml
        - application/json
      parameters:
        - in: body
          name: body
          description: List of user object
          required: false
          schema:
            type: array
            items:
              $ref: "#/definitions/User"
      responses:
        default:
          description: successful operation
  /user/login:
    get:
      tags:
        - user
      summary: Logs user into the system
      description: ""
      operationId: loginUser
      produces:
        - application/xml
        - application/json
      parameters:
        - name: username
          in: query
          description: The user name for login
          required: false
          type: string
        - name: password
          in: query
          description: The password for login in clear text
          required: false
          type: string
      responses:
        "200":
          description: successful operation
          schema:
            type: string
          headers:
            X-Rate-Limit:
              type: integer
              format: int32
              description: calls per hour allowed by the user
            X-Expires-After:
              type: string
              format: date-time
              description: date in UTC when toekn expires
        "400":
          description: Invalid username/password supplied
  /user/logout:
    get:
      tags:
        - user
      summary: Logs out current logged in user session
      description: ""
      operationId: logoutUser
      produces:
        - application/xml
        - application/json
      parameters: []
      responses:
        default:
          description: successful operation
  "/user/{username}":
    get:
      tags:
        - user
      summary: Get user by user name
      description: ""
      operationId: getUserByName
      produces:
        - application/xml
        - application/json
      parameters:
        - name: username
          in: path
          description: "The name that needs to be fetched. Use user1 for testing. "
          required: true
          type: string
      responses:
        "200":
          description: successful operation
          schema:
            $ref: "#/definitions/User"
        "400":
          description: Invalid username supplied
        "404":
          description: User not found
    put:
      tags:
        - user
      summary: Updated user
      description: This can only be done by the logged in user.
      operationId: updateUser
      produces:
        - application/xml
        - application/json
      parameters:
        - name: username
          in: path
          description: name that need to be deleted
          required: true
          type: string
        - in: body
          name: body
          description: Updated user object
          required: false
          schema:
            $ref: "#/definitions/User"
      responses:
        "400":
          description: Invalid user supplied
        "404":
          description: User not found
    delete:
      tags:
        - user
      summary: Delete user
      description: This can only be done by the logged in user.
      operationId: deleteUser
      produces:
        - application/xml
        - application/json
      parameters:
        - name: username
          in: path
          description: The name that needs to be deleted
          required: true
          type: string
      responses:
        "400":
          description: Invalid username supplied
        "404":
          description: User not found
securityDefinitions:
  petstore_auth:
    type: oauth2
    authorizationUrl: "http://petstore.swagger.io/api/oauth/dialog"
    flow: implicit
    scopes:
      "write:pets": modify pets in your account
      "read:pets": read your pets
  api_key:
    type: apiKey
    name: api_key
    in: header
definitions:
  Order:
    properties:
      id:
        type: integer
        format: int64
      petId:
        type: integer
        format: int64
      quantity:
        type: integer
        format: int32
      shipDate:
        type: string
        format: date-time
      status:
        type: string
        description: Order Status
        enum:
          - placed
          - approved
          - delivered
      complete:
        type: boolean
    xml:
      name: Order
  Category:
    properties:
      id:
        type: integer
        format: int64
      name:
        type: string
    xml:
      name: Category
  User:
    properties:
      id:
        type: integer
        format: int64
      username:
        type: string
      firstName:
        type: string
      lastName:
        type: string
      email:
        type: string
      password:
        type: string
      phone:
        type: string
      userStatus:
        type: integer
        format: int32
        description: User Status
    xml:
      name: User
  Tag:
    properties:
      id:
        type: integer
        format: int64
      name:
        type: string
    xml:
      name: Tag
  Pet:
    required:
      - name
      - photoUrls
    properties:
      id:
        type: integer
        format: int64
      category:
        $ref: "#/definitions/Category"
      name:
        type: string
        example: doggie
      photoUrls:
        type: array
        xml:
          name: photoUrl
          wrapped: true
        items:
          type: string
      tags:
        type: array
        xml:
          name: tag
          wrapped: true
        items:
          $ref: "#/definitions/Tag"
      status:
        type: string
        description: pet status in the store
        enum:
          - available
          - pending
          - sold
    xml:
      name: Pet
  ApiResponse:
    properties:
      code:
        type: integer
        format: int32
      type:
        type: string
      message:
        type: string
    xml:
      name: "##default"
externalDocs:
  description: Find out more about Swagger
  url: "http://swagger.io"


}

'''
@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/swagger', methods=['GET'])
def generateERResponseFromSwaggerUsingCohere():

    print('analyze_text')
    print('before cohere')
    co = cohere.Client('80OIPP2omIsbrQx5ONqCZCw3Xq2EKT74nxkee70R') # This is your trial API key
    response = co.generate(
        model='command',
        prompt=prompt,
        temperature=0.9,
        k=0,
        stop_sequences=[],
        return_likelihoods='NONE')
    print(response)
    return response.generations[0].text

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request)
    print(request.files)
    if len(request.files) == 0:
        return 'No files uploaded'
    
    if 'file' not in request.files:
        return 'No file part'
    
    print(request)
    print(request.files)

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    # Process the file as needed (save, analyze, etc.)
    # For example, save the file to the server
    file.save('uploaded_file.txt')

    return 'File successfully uploaded'

@app.route('/upload-test', methods=['POST'])
def upload_file2():
    print(request.data)
    if len(request.files) == 0:
        return 'No files uploaded'
    
    if 'file' not in request.files:
        return 'No file part'
    
    print(request)
    print(request.files)

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    # Process the file as needed (save, analyze, etc.)
    # For example, save the file to the server
    file.save('uploaded_file.txt')

    return 'File successfully uploaded'

""""@app.route('/test')
def generate_er_diagram():
    # Generate ER diagram using Graphviz

    entities = {
    'Pet': ['id', 'name', 'photo_urls', 'category', 'tags', 'status'],
    'Category': ['id', 'name'],
    'Tag': ['id', 'name'],
    'Order': ['id', 'pet_id', 'quantity', 'ship_date', 'status', 'complete'],
    'User': ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'phone', 'user_status']
    }

    relationships = [
    ('Pet', 'Tag', 'one_to_many'),
    ('Category', 'Pet', 'one_to_many'),
    ('Tag', 'Pet', 'one_to_many'),
    ('Order', 'User', 'one_to_one'),
    ('User', 'Order', 'one_to_many')
    ]

    graph = Digraph(comment='ER Diagram')
    for entity, attributes in entities.items():
        graph.node(entity, shape='box', label=f"{entity}\n{', '.join(attributes)}")

    for relationship in relationships:
        graph.edge(relationship[0], relationship[1], label=relationship[2])

    print(graph)
    # Save the graph as PNG
    # Get the directory of the script
    # script_directory = os.path.dirname(os.path.realpath(__file__))
    # print(script_directory)

    # Set the file path to the same directory with a relative path
    # graph_file_path = os.path.join(script_directory, 'er_diagram')
    # print(graph_file_path)
    graph_file_path = '/tmp/er_diagram'
    print(graph_file_path)
    graph.render(graph_file_path,format='png',cleanup=True)
    # Open the PNG file and convert to response
    img = Image.open(graph_file_path +'.png')
    print(img)
    response = send_file(graph_file_path +'.png', mimetype='image/png', as_attachment=True, download_name='er_diagram.png')
    print(response)
    return response"""

@app.route('/ER', methods=['POST'])
def generateERResponseFromSwaggerUsingOpenAI():
    uploaded_file = request.files['file']

    if uploaded_file:
        # Read the content of the file as a string
        file_content_bytes = uploaded_file.read()
        file_content_string = file_content_bytes.decode('utf-8')
        print(file_content_string)
    
    prompt = '''generate Entity Relationship Model in the following format :
entities = {
    'entity1': ['id', ....],
     'entity2': ['id', ....],
}
relationships = [
    ('entity1', 'entity2', 'many_to_many'),
    ('entity2', 'entity1', 'one_to_many')
]
where entity1, entity2 are examples names to give you as an example. Please change them accordingly and give the reponse json format. 

from swagger yaml given below:''' + file_content_string
    
    api_key = os.environ.get("OPENAI_API_KEY")  # Replace 'your-api-key' with your actual API key
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    #print(response)
    print(response.choices[0].message.content)
    print(type(response.choices[0].message.content))
    return response.choices[0].message.content


@app.route('/test-produce-bugs', methods=['GET'])
def testForProducingBugs():
    a=[]
    print(a[1]);

@app.route('/upload-zip', methods=['POST'])
def upload_zip():
    # Check if the POST request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    zip_file = request.files['file']

    print(zip_file)

    # Check if the file has a name and ends with .zip
    if zip_file.filename == '' or not zip_file.filename.endswith('.zip'):
        return jsonify({'error': 'Invalid file format. Please upload a .zip file'}), 400

    try:
        # Read the zip file contents into memory
        zip_data = io.BytesIO(zip_file.read())

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            file_contents = {}
            api_key = os.environ.get("OPENAI_API_KEY")  # Replace 'your-api-key' with your actual API key
            client = OpenAI(api_key=api_key)
            messages=[{"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                      {"role": "user", "content": "Please analyze the the java project which I will be sending each file one by one along with the file path"}]
          
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={ "type": "json_object" },
                messages=messages,
                temperature=1,
                max_tokens=4096,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
              )
            print(response.choices[0].message.content)
            ob={"role": "assistant", "content": response.choices[0].message.content}
            messages.append(ob);
            print("messages ", messages)
            for file_info in zip_ref.infolist():
                with zip_ref.open(file_info) as file:
                    content = file.read().decode('utf-8')
                    file_contents[file_info.filename] = content
                    ob={"role": "user", "content": "analyze the code its file path is "+file_info.filename+ " and its code is "+ content}
                    messages.append(ob);
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        response_format={ "type": "json_object" },
                        messages=messages,
                        temperature=1,
                        max_tokens=4096,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                      )
                    print(response.choices[0].message.content)
                    ob={"role": "assistant", "content": response.choices[0].message.content}
                    messages.append(ob)
            ob={"role": "user", "content": "please summerize the whole java project by using the code the file paths provided in the previous prompts"}
            messages.append(ob)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={ "type": "json_object" },
                messages=messages,
                temperature=1,
                max_tokens=4096,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
              ) 
            
            print(response.choices[0].message.content)
            return response.choices[0].message.content

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    testForProducingBugs()