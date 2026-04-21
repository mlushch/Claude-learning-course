using Microsoft.AspNetCore.Mvc;
using TaskManager.Api.DTOs;
using TaskManager.Api.Models;
using TaskManager.Api.Repositories;

namespace TaskManager.Api.Controllers;

[ApiController]
[Route("tasks")]
public class TasksController(ITaskRepository repo) : ControllerBase
{
    [HttpGet]
    public IActionResult GetAll([FromQuery] string? status)
    {
        var tasks = repo.GetAll();
        if (status is not null && Enum.TryParse<TaskItemStatus>(status, ignoreCase: true, out var parsed))
            tasks = tasks.Where(t => t.Status == parsed);
        return Ok(tasks);
    }

    [HttpGet("{id:guid}")]
    public IActionResult GetById(Guid id)
    {
        var task = repo.GetById(id);
        return task is null ? NotFound() : Ok(task);
    }

    [HttpPost]
    public IActionResult Create([FromBody] CreateTaskDto dto)
    {
        var task = new TaskItem
        {
            Title = dto.Title,
            Description = dto.Description,
            Priority = dto.Priority,
            DueDate = dto.DueDate
        };
        repo.Add(task);
        return CreatedAtAction(nameof(GetById), new { id = task.Id }, task);
    }

    [HttpPut("{id:guid}")]
    public IActionResult Update(Guid id, [FromBody] UpdateTaskDto dto)
    {
        var existing = repo.GetById(id);
        if (existing is null) return NotFound();

        existing.Title = dto.Title;
        existing.Description = dto.Description;
        existing.Status = dto.Status;
        existing.Priority = dto.Priority;
        existing.DueDate = dto.DueDate;

        repo.Update(id, existing);
        return Ok(existing);
    }

    [HttpDelete("{id:guid}")]
    public IActionResult Delete(Guid id)
    {
        return repo.Delete(id) ? NoContent() : NotFound();
    }
}
