using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using TaskManager.Api.Models;

namespace TaskManager.Api.Tests;

public class TasksControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly HttpClient _unauthClient;
    private const string ApiKey = "dev-secret-key-change-me";

    public TasksControllerTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
        _client.DefaultRequestHeaders.Add("X-Api-Key", ApiKey);
        _unauthClient = factory.CreateClient();
    }

    // ── GET /tasks ──────────────────────────────────────────────────────────

    [Fact]
    public async Task GetAll_ReturnsEmptyList_WhenNoTasksExist()
    {
        var response = await _client.GetAsync("/tasks");
        response.EnsureSuccessStatusCode();
        var tasks = await response.Content.ReadFromJsonAsync<List<object>>();
        Assert.NotNull(tasks);
    }

    [Fact]
    public async Task GetAll_FiltersByStatus_WhenStatusProvided()
    {
        await _client.PostAsJsonAsync("/tasks", new { title = "Filter test", priority = "High" });
        var response = await _client.GetAsync("/tasks?status=Open");
        response.EnsureSuccessStatusCode();
        var tasks = await response.Content.ReadFromJsonAsync<List<Dictionary<string, object>>>();
        Assert.NotNull(tasks);
        Assert.All(tasks, t => Assert.Equal("Open", t["status"].ToString()));
    }

    // ── POST /tasks ──────────────────────────────────────────────────────────

    [Fact]
    public async Task Create_Returns201_WithValidInput()
    {
        var response = await _client.PostAsJsonAsync("/tasks",
            new { title = "Test task", priority = "High" });
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        Assert.NotNull(response.Headers.Location);
    }

    [Fact]
    public async Task Create_Returns400_WhenTitleMissing()
    {
        var response = await _client.PostAsJsonAsync("/tasks",
            new { description = "no title" });
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task Create_Returns400_WhenTitleTooLong()
    {
        var response = await _client.PostAsJsonAsync("/tasks",
            new { title = new string('x', 201) });
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    // ── GET /tasks/{id} ──────────────────────────────────────────────────────

    [Fact]
    public async Task GetById_ReturnsTask_WhenFound()
    {
        var created = await _client.PostAsJsonAsync("/tasks", new { title = "Find me" });
        var task = await created.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        var id = task!["id"];

        var response = await _client.GetAsync($"/tasks/{id}");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    [Fact]
    public async Task GetById_Returns404_WhenNotFound()
    {
        var response = await _client.GetAsync($"/tasks/{Guid.NewGuid()}");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    // ── PUT /tasks/{id} ──────────────────────────────────────────────────────

    [Fact]
    public async Task Update_UpdatesTask_WhenFound()
    {
        var created = await _client.PostAsJsonAsync("/tasks", new { title = "Original" });
        var task = await created.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        var id = task!["id"];

        var response = await _client.PutAsJsonAsync($"/tasks/{id}",
            new { title = "Updated", status = "InProgress", priority = "High" });
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var updated = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        Assert.Equal("Updated", updated!["title"].ToString());
        Assert.Equal("InProgress", updated["status"].ToString());
    }

    [Fact]
    public async Task Update_Returns404_WhenNotFound()
    {
        var response = await _client.PutAsJsonAsync($"/tasks/{Guid.NewGuid()}",
            new { title = "X", status = "Open", priority = "Low" });
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    // ── DELETE /tasks/{id} ──────────────────────────────────────────────────

    [Fact]
    public async Task Delete_RemovesTask_WhenFound()
    {
        var created = await _client.PostAsJsonAsync("/tasks", new { title = "Delete me" });
        var task = await created.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        var id = task!["id"];

        var response = await _client.DeleteAsync($"/tasks/{id}");
        Assert.Equal(HttpStatusCode.NoContent, response.StatusCode);
    }

    [Fact]
    public async Task Delete_Returns404_WhenNotFound()
    {
        var response = await _client.DeleteAsync($"/tasks/{Guid.NewGuid()}");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    // ── Auth ──────────────────────────────────────────────────────────────────

    [Fact]
    public async Task AnyEndpoint_Returns401_WhenApiKeyMissing()
    {
        var response = await _unauthClient.GetAsync("/tasks");
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task AnyEndpoint_Returns401_WhenApiKeyWrong()
    {
        _unauthClient.DefaultRequestHeaders.Add("X-Api-Key", "wrong-key");
        var response = await _unauthClient.GetAsync("/tasks");
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task Health_Returns200_WithoutApiKey()
    {
        var response = await _unauthClient.GetAsync("/health");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }
}
