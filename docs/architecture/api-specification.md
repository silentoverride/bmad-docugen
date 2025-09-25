# API Specification
```yaml
openapi: 3.1.0
info:
  title: DocuGen Bundle API
  version: v1
  description: |
    REST interface powering DocuGen CLI, admin UI, and partner integrations. All endpoints require OAuth2 access tokens issued by Keycloak.
servers:
  - url: http://localhost:8080
    description: Local Docker Compose environment
  - url: https://api.docugen.local
    description: Tunnelled host URL for remote testing
paths:
  /api/v1/configurations:
    post:
      summary: Create a configuration set
      description: Normalises bundle inputs, account selections, and rendering options for deterministic reuse.
      tags: [Configurations]
      security:
        - oauth:
            - bundle.write
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateConfigurationRequest'
            examples:
              default:
                value:
                  seedSource: uploaded
                  seedPayload:
                    applicant:
                      fullName: "Jane Citizen"
                      dateOfBirth: "1991-03-08"
                    accounts:
                      - institution: NAB
                        bsb: "082-001"
                        accountNumber: "12345678"
                        currency: AUD
                  accounts:
                    - accountId: "primary-cheque"
                      periods:
                        - from: "2025-05-01"
                          to: "2025-07-31"
                  renderOptions:
                    locale: en-AU
                    includeWatermark: false
      responses:
        '201':
          description: Configuration created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConfigurationSet'
        '400':
          $ref: '#/components/responses/ValidationError'
    get:
      summary: List configuration sets
      tags: [Configurations]
      security:
        - oauth:
            - bundle.read
      parameters:
        - in: query
          name: seedSource
          schema:
            $ref: '#/components/schemas/SeedSource'
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: Paginated configuration sets
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConfigurationSetPage'

  /api/v1/configurations/{configurationId}:
    get:
      summary: Fetch configuration details
      tags: [Configurations]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/ConfigurationId'
      responses:
        '200':
          description: Configuration definition
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConfigurationSet'
        '404':
          $ref: '#/components/responses/NotFound'

  /api/v1/bundles:
    post:
      summary: Launch a document bundle run
      tags: [Bundles]
      security:
        - oauth:
            - bundle.write
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LaunchBundleRequest'
            examples:
              default:
                value:
                  configurationId: "cfg_9b7e9d5b"
                  seedHash: "28c21c..."
                  forcingOptions:
                    skipValidations: false
      responses:
        '202':
          description: Bundle accepted for processing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DocumentBundleRun'
    get:
      summary: List bundle runs
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - in: query
          name: status
          schema:
            $ref: '#/components/schemas/BundleStatus'
        - in: query
          name: since
          schema:
            type: string
            format: date-time
        - in: query
          name: limit
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Paginated bundles
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BundleRunPage'

  /api/v1/bundles/{bundleId}:
    get:
      summary: Get bundle status summary
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Bundle run
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DocumentBundleRun'
        '404':
          $ref: '#/components/responses/NotFound'

  /api/v1/bundles/{bundleId}/artefacts:
    get:
      summary: List generated artefacts for a bundle
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Artefact collection
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ArtefactList'

  /api/v1/bundles/{bundleId}/manifest:
    get:
      summary: Retrieve signed manifest metadata
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Manifest information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Manifest'

  /api/v1/bundles/{bundleId}/validations:
    get:
      summary: Fetch validation results for a bundle
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Validation results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationList'

  /api/v1/merchants/search:
    get:
      summary: Search cached merchant/employer profiles
      tags: [Reference Data]
      security:
        - oauth:
            - reference.read
      parameters:
        - in: query
          name: q
          required: true
          schema:
            type: string
            minLength: 2
        - in: query
          name: includePlacesLookup
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Matching merchants/employers
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MerchantSearchResponse'

  /api/v1/webhooks/run-events:
    post:
      summary: Receive bundle lifecycle events
      description: Partners register a signed webhook endpoint to mirror EventBridge notifications.
      tags: [Integrations]
      security:
        - webhookSignature: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RunEvent'
      responses:
        '204':
          description: Event accepted

components:
  securitySchemes:
    oauth:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: http://localhost:8080/auth/realms/docugen/protocol/openid-connect/auth
          tokenUrl: http://localhost:8080/auth/realms/docugen/protocol/openid-connect/token
          scopes:
            bundle.read: Read bundle information
            bundle.write: Trigger bundles and manage configurations
            reference.read: Access cached merchant data
        deviceCode:
          authorizationUrl: http://localhost:8080/auth/realms/docugen/device
          tokenUrl: http://localhost:8080/auth/realms/docugen/protocol/openid-connect/token
          scopes:
            bundle.read: Read bundle information
            bundle.write: Trigger bundles and manage configurations
    webhookSignature:
      type: http
      scheme: bearer
      bearerFormat: HMAC-SHA256 signature header

  parameters:
    BundleId:
      in: path
      name: bundleId
      required: true
      schema:
        type: string
        format: uuid
    ConfigurationId:
      in: path
      name: configurationId
      required: true
      schema:
        type: string
        format: uuid

  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    ValidationError:
      description: Request failed validation
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationErrorResponse'

  schemas:
    SeedSource:
      type: string
      enum: [uploaded, fixture, api]
    ActorRef:
      type: object
      required: [type, id]
      properties:
        type:
          type: string
          enum: [cli-user, admin-user, automation]
        id:
          type: string
    RunParameters:
      type: object
      properties:
        selectedAccounts:
          type: array
          items:
            type: string
        includeWatermark:
          type: boolean
        locale:
          type: string
          default: en-AU
    CreateConfigurationRequest:
      type: object
      required: [seedSource, seedPayload, accounts]
      properties:
        seedSource:
          $ref: '#/components/schemas/SeedSource'
        seedPayload:
          type: object
          description: Structured applicant/account payload as per CLI schema.
        accounts:
          type: array
          items:
            type: object
            required: [accountId, periods]
            properties:
              accountId:
                type: string
              periods:
                type: array
                items:
                  type: object
                  required: [from, to]
                  properties:
                    from:
                      type: string
                      format: date
                    to:
                      type: string
                      format: date
        renderOptions:
          type: object
          properties:
            locale:
              type: string
              default: en-AU
            includeWatermark:
              type: boolean
              default: false
            outputFormat:
              type: string
              enum: [pdf, pdf_and_json]
    ConfigurationSet:
      type: object
      required: [id, seedSource, accounts, renderOptions, createdBy]
      properties:
        id:
          type: string
          format: uuid
        seedSource:
          $ref: '#/components/schemas/SeedSource'
        accounts:
          type: array
          items:
            type: object
            properties:
              accountId:
                type: string
              periods:
                type: array
                items:
                  type: object
                  properties:
                    from:
                      type: string
                      format: date
                    to:
                      type: string
                      format: date
        renderOptions:
          type: object
          properties:
            locale:
              type: string
            includeWatermark:
              type: boolean
            outputFormat:
              type: string
        createdBy:
          $ref: '#/components/schemas/ActorRef'
        createdAt:
          type: string
          format: date-time
    ConfigurationSetPage:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/ConfigurationSet'
        nextCursor:
          type: string
          nullable: true
    LaunchBundleRequest:
      type: object
      required: [configurationId]
      properties:
        configurationId:
          type: string
          format: uuid
        seedHash:
          type: string
          description: Optional pre-computed hash for deterministic replay.
        forcingOptions:
          type: object
          properties:
            skipValidations:
              type: boolean
            replayRunId:
              type: string
              format: uuid
    BundleStatus:
      type: string
      enum: [pending, running, completed, failed, blocked]
    DocumentBundleRun:
      type: object
      required: [id, status, triggeredBy, startedAt, manifestId, runParameters]
      properties:
        id:
          type: string
          format: uuid
        status:
          $ref: '#/components/schemas/BundleStatus'
        triggeredBy:
          $ref: '#/components/schemas/ActorRef'
        startedAt:
          type: string
          format: date-time
        completedAt:
          type: string
          format: date-time
          nullable: true
        manifestId:
          type: string
          format: uuid
        configurationId:
          type: string
          format: uuid
        runParameters:
          $ref: '#/components/schemas/RunParameters'
    BundleRunPage:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/DocumentBundleRun'
        nextCursor:
          type: string
          nullable: true
    DocumentArtefact:
      type: object
      required: [id, type, storageKey, checksum, renderVersion]
      properties:
        id:
          type: string
          format: uuid
        type:
          type: string
          enum: [bank_statement, payslip, proof_of_balance]
        storageKey:
          type: string
        checksum:
          type: string
        renderVersion:
          type: string
    ArtefactList:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/DocumentArtefact'
        presignedUrls:
          type: object
          additionalProperties:
            type: string
    Manifest:
      type: object
      required: [id, bundleRunId, hash, signature, signingKeyId, createdAt]
      properties:
        id:
          type: string
          format: uuid
        bundleRunId:
          type: string
          format: uuid
        hash:
          type: string
        signature:
          type: string
        signingKeyId:
          type: string
        createdAt:
          type: string
          format: date-time
        metadata:
          type: object
    ValidationResult:
      type: object
      required: [id, ruleCode, severity, status, details]
      properties:
        id:
          type: string
          format: uuid
        ruleCode:
          type: string
        severity:
          type: string
          enum: [info, warning, error]
        status:
          type: string
          enum: [pass, fail, blocked]
        details:
          type: object
    ValidationList:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/ValidationResult'
    MerchantSearchResponse:
      type: object
      properties:
        items:
          type: array
          items:
            type: object
            required: [id, name]
            properties:
              id:
                type: string
                format: uuid
              name:
                type: string
              category:
                type: string
              placesId:
                type: string
                nullable: true
              address:
                type: object
    RunEvent:
      type: object
      required: [bundleId, event, emittedAt]
      properties:
        bundleId:
          type: string
          format: uuid
        event:
          type: string
          enum: [RUN_STARTED, VALIDATION_FAILED, RUN_COMPLETED, MANIFEST_SIGNED]
        emittedAt:
          type: string
          format: date-time
        payload:
          type: object
    ErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, requestId]
          properties:
            code:
              type: string
            message:
              type: string
            requestId:
              type: string
    ValidationErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, violations]
          properties:
            code:
              type: string
              example: VALIDATION_FAILED
            message:
              type: string
            violations:
              type: array
              items:
                type: object
                required: [field, issue]
                properties:
                  field:
                    type: string
                  issue:
                    type: string
```
