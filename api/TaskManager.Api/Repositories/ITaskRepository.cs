using TaskManager.Api.Models;

namespace TaskManager.Api.Repositories;

public interface ITaskRepository
{
    IEnumerable<TaskItem> GetAll();
    TaskItem? GetById(Guid id);
    TaskItem Add(TaskItem task);
    TaskItem? Update(Guid id, TaskItem task);
    bool Delete(Guid id);
}
