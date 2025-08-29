interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export function FormInput({ label, className = "", ...props }: FormInputProps) {
  const inputClass = `border p-2 rounded ${className}`;
  
  if (label) {
    return (
      <div>
        <label className="block text-sm font-medium mb-1">{label}</label>
        <input className={inputClass} {...props} />
      </div>
    );
  }
  
  return <input className={inputClass} {...props} />;
}

export function FormSelect({ label, className = "", children, ...props }: any) {
  const selectClass = `border p-2 rounded ${className}`;
  return label ? (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <select className={selectClass} {...props}>{children}</select>
    </div>
  ) : (
    <select className={selectClass} {...props}>{children}</select>
  );
}
