using System.ComponentModel.DataAnnotations;
using TaskManager.Api.Models;

namespace TaskManager.Api.DTOs;

public record CreateTaskDto(
    [Required][MaxLength(200)] string Title,
    [MaxLength(2000)] string? Description,
    TaskPriority Priority = TaskPriority.Medium,
    DateTime? DueDate = null
);

public record UpdateTaskDto(
    [MaxLength(200)] string? Title,
    [MaxLength(2000)] string? Description,
    TaskItemStatus? Status,
    TaskPriority? Priority,
    DateTime? DueDate
);
