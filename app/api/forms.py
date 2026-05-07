from django import forms
from .models import Livro, Membro, Editora, Emprestimo

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'isbn', 'paginas', 'ano_publicacao', 'editora']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do Livro'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Autor'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN'}),
            'paginas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de Páginas'}),
            'ano_publicacao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ano de Publicação'}),
            'editora': forms.Select(attrs={'class': 'form-control'}),
        }

class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ['nome', 'email', 'telefone', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EditoraForm(forms.ModelForm):
    class Meta:
        model = Editora
        fields = ['nome', 'site', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Editora'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail de Contato'}),
        }

class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['membro', 'livro', 'data_devolucao']
        widgets = {
            'membro': forms.Select(attrs={'class': 'form-control'}),
            'livro': forms.Select(attrs={'class': 'form-control'}),
            'data_devolucao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
