using System.Collections.Concurrent;
using TaskManager.Api.Models;

namespace TaskManager.Api.Repositories;

public class InMemoryTaskRepository : ITaskRepository
{
    private readonly ConcurrentDictionary<Guid, TaskItem> _tasks = new();

    public IEnumerable<TaskItem> GetAll() => _tasks.Values;

    public TaskItem? GetById(Guid id) =>
        _tasks.TryGetValue(id, out var task) ? task : null;

    public TaskItem Add(TaskItem task)
    {
        _tasks[task.Id] = task;
        return task;
    }

    public TaskItem? Update(Guid id, TaskItem updated)
    {
        if (!_tasks.ContainsKey(id)) return null;
        _tasks[id] = updated;
        return updated;
    }

    public bool Delete(Guid id) => _tasks.TryRemove(id, out _);
}
