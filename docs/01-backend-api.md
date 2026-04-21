# Step 1: Backend API (C# / ASP.NET Core)

## Goal

Build a REST API with full CRUD for tasks, API Key authentication, and basic input validation.

---

## 1.1 Project Setup

```bash
# Create solution and projects
dotnet new sln -n TaskManager
dotnet new webapi -n TaskManager.Api --no-openapi false
dotnet new xunit -n TaskManager.Api.Tests
dotnet sln add TaskManager.Api/TaskManager.Api.csproj
dotnet sln add TaskManager.Api.Tests/TaskManager.Api.Tests.csproj
dotnet add TaskManager.Api.Tests reference TaskManager.Api/TaskManager.Api.csproj
```

Place all of this under `api/`.

---

## 1.2 Task Model

File: `TaskManager.Api/Models/TaskItem.cs`

```csharp
public class TaskItem
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Title { get; set; } = string.Empty;       // required, max 200 chars
    public string? Description { get; set; }
    public TaskStatus Status { get; set; } = TaskStatus.Open;
    public TaskPriority Priority { get; set; } = TaskPriority.Medium;
    public DateTime? DueDate { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public enum TaskStatus  { Open, InProgress, Completed }
public enum TaskPriority { Low, Medium, High }
```

---

## 1.3 In-Memory Repository

File: `TaskManager.Api/Repositories/ITaskRepository.cs` + `InMemoryTaskRepository.cs`

```csharp
public interface ITaskRepository
{
    IEnumerable<TaskItem> GetAll();
    TaskItem? GetById(Guid id);
    TaskItem Add(TaskItem task);
    TaskItem? Update(Guid id, TaskItem task);
    bool Delete(Guid id);
}
```

`InMemoryTaskRepository` uses a `ConcurrentDictionary<Guid, TaskItem>` — no database needed for the MVP.

---

## 1.4 API Key Middleware

File: `TaskManager.Api/Middleware/ApiKeyMiddleware.cs`

- Read expected key from `appsettings.json` → `ApiKey` field
- Check incoming `X-Api-Key` header on every request
- Return `401 Unauthorized` if missing or wrong
- Skip middleware for `/health` endpoint

```json
// appsettings.json
{
  "ApiKey": "dev-secret-key-change-me"
}
```

Register in `Program.cs`:
```csharp
app.UseMiddleware<ApiKeyMiddleware>();
```

---

## 1.5 Tasks Controller

File: `TaskManager.Api/Controllers/TasksController.cs`

| Method | Route              | Description             | Body / Params          |
|--------|--------------------|-------------------------|------------------------|
| GET    | `/tasks`           | List all tasks          | Optional `?status=`    |
| GET    | `/tasks/{id}`      | Get single task         | —                      |
| POST   | `/tasks`           | Create task             | `CreateTaskDto`        |
| PUT    | `/tasks/{id}`      | Full update             | `UpdateTaskDto`        |
| DELETE | `/tasks/{id}`      | Delete task             | —                      |

**DTOs with validation:**

```csharp
public record CreateTaskDto(
    [Required][MaxLength(200)] string Title,
    string? Description,
    TaskPriority Priority = TaskPriority.Medium,
    DateTime? DueDate = null
);

public record UpdateTaskDto(
    [Required][MaxLength(200)] string Title,
    string? Description,
    TaskStatus Status,
    TaskPriority Priority,
    DateTime? DueDate
);
```

Return `404` when task not found, `400` on validation failure, `201 Created` with `Location` header on create.

---

## 1.6 Health Endpoint

```csharp
app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));
```

---

## 1.7 CORS & Swagger

Enable Swagger UI in development. Enable CORS for local MCP server calls.

---

## 1.8 Validation Checklist

- [ ] `GET /tasks` returns empty list when no tasks exist
- [ ] `POST /tasks` with missing `Title` returns `400`
- [ ] `POST /tasks` with valid body returns `201` + task JSON
- [ ] `GET /tasks/{id}` with unknown id returns `404`
- [ ] `PUT /tasks/{id}` updates fields correctly
- [ ] `DELETE /tasks/{id}` removes the task
- [ ] Any request without `X-Api-Key` header returns `401`
- [ ] Wrong `X-Api-Key` value returns `401`
- [ ] `/health` works without API key

---

## 1.9 Run Locally

```bash
cd api/TaskManager.Api
dotnet run
# API available at http://localhost:5000
```

Test with curl:
```bash
curl -H "X-Api-Key: dev-secret-key-change-me" http://localhost:5000/tasks
```
