export default function CommentThread({ comments }) {
  if (comments.length === 0) {
    return <p className="text-sm text-gray-400">No comments yet.</p>
  }

  return (
    <ul className="space-y-3">
      {comments.map((comment) => (
        <li key={comment.id} className="rounded-lg border border-gray-200 bg-gray-50 p-3">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="font-medium text-gray-900">{comment.author_name}</span>
            <span className="rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-600">
              {comment.author_role === 'support_agent' ? 'Support Agent' : 'Employee'}
            </span>
            <span className="text-xs text-gray-400">
              {new Date(comment.created_at).toLocaleString()}
            </span>
          </div>
          <p className="mt-1 whitespace-pre-wrap text-sm text-gray-700">{comment.content}</p>
        </li>
      ))}
    </ul>
  )
}
