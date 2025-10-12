# Диаграмма классов

classDiagram
    %% Основной класс пользователя
    class User {
        -String username
        -String email
        -String passwordHash
        -String activatorCode
        -UserRole role
        -DateTime registrationDate
        -DateTime lastLogin
        +login()
        +logout()
        +changePassword()
        +validateActivator()
        +upgradeRole()
    }

    %% Классы пользователей с наследованием
    class Observer {
        -List~Report~ accessibleReports
        -List~Video~ accessibleVideos
        +viewReports()
        +searchReports()
        +filterReports()
        +exportReport()
        +viewVideoLibrary()
    }

    class Analyst {
        -List~Model~ accessibleModels
        -List~AnalysisConfig~ analysisConfigs
        +modifyAlgorithms()
        +changeReportFormat()
        +analyzeCustomVideo()
        +compareReports()
        +batchProcessVideos()
        +configureAnalysis()
        +visualizeResults()
        +compareModels()
        +createReport()
        +modifyReport()
        +deleteReport()
        +addTrainingVideo()
    }

    class Administrator {
        -List~User~ managedUsers
        -String masterActivator
        +createUser()
        +editUser()
        +blockUser()
        +assignRole()
        +uploadModel()
        +manageModelVersions()
        +monitorPerformance()
        +setupABTesting()
        +systemMonitoring()
        +backupManagement()
        +auditLogs()
        +generateActivator()
        +revokeAnalystRights()
    }

    %% Новый класс для управления активаторами
    class ActivatorManager {
        -Map~String, String~ validActivators
        -int activatorExpiryDays
        +generateActivator()
        +validateActivator()
        +revokeActivator()
        +getActivatorStatus()
    }

    %% Перечисления
    class UserRole {
        <<enumeration>>
        OBSERVER
        ANALYST
        ADMINISTRATOR
    }

    %% Связи наследования
    User <|-- Observer
    User <|-- Analyst
    Analyst <|-- Administrator

    %% Ассоциации
    Administrator "1" -- "1" ActivatorManager : manages
    User "1" -- "1" ActivatorManager : validates