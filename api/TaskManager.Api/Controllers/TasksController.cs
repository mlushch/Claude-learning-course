using Microsoft.AspNetCore.Mvc;
using TaskManager.Api.DTOs;
using TaskManager.Api.Models;
using TaskManager.Api.Repositories;

namespace TaskManager.Api.Controllers;

[ApiController]
[Route("tasks")]
[Produces("application/json")]
public class TasksController(ITaskRepository repo) : ControllerBase
{
    [HttpGet]
    [ProducesResponseType<IEnumerable<TaskItem>>(StatusCodes.Status200OK)]
    public ActionResult<IEnumerable<TaskItem>> GetAll([FromQuery] string? status)
    {
        var tasks = repo.GetAll();
        if (status is not null && Enum.TryParse<TaskItemStatus>(status, ignoreCase: true, out var parsed))
            tasks = tasks.Where(t => t.Status == parsed);
        return Ok(tasks);
    }

    [HttpGet("{id:guid}")]
    [ProducesResponseType<TaskItem>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult<TaskItem> GetById(Guid id)
    {
        var task = repo.GetById(id);
        return task is null ? NotFound() : Ok(task);
    }

    [HttpPost]
    [ProducesResponseType<TaskItem>(StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public ActionResult<TaskItem> Create([FromBody] CreateTaskDto dto)
    {
        var task = new TaskItem
        {
            Title = dto.Title,
            Description = dto.Description,
            Priority = dto.Priority,
            DueDate = dto.DueDate,
        };
        repo.Add(task);
        return CreatedAtAction(nameof(GetById), new { id = task.Id }, task);
    }

    [HttpPut("{id:guid}")]
    [ProducesResponseType<TaskItem>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult<TaskItem> Update(Guid id, [FromBody] UpdateTaskDto dto)
    {
        var existing = repo.GetById(id);
        if (existing is null) return NotFound();

        var updated = existing with
        {
            Title = dto.Title,
            Description = dto.Description,
            Status = dto.Status,
            Priority = dto.Priority,
            DueDate = dto.DueDate,
        };

        repo.Update(id, updated);
        return Ok(updated);
    }

    [HttpDelete("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public IActionResult Delete(Guid id)
    {
        return repo.Delete(id) ? NoContent() : NotFound();
    }
}
