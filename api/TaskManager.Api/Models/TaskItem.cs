namespace TaskManager.Api.Models;

public record TaskItem
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public string Title { get; init; } = string.Empty;
    public string? Description { get; init; }
    public TaskItemStatus Status { get; init; } = TaskItemStatus.Open;
    public TaskPriority Priority { get; init; } = TaskPriority.Medium;
    public DateTime? DueDate { get; init; }
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;
}

public enum TaskItemStatus { Open, InProgress, Completed }
public enum TaskPriority { Low, Medium, High }
