// Preços por tipo de quarto
const PRECOS = {
    'solteiro': 700,  
    'casal': 1200,   
    'luxo': 2000    
};



document.addEventListener('DOMContentLoaded', function() {

    const entrySelect = document.getElementById('entry_date');
    const exitSelect = document.getElementById('exit_date');
    const roomTypeSelect = document.getElementById('room_type');
    const valorTotalSpan = document.getElementById('valor_total');
    const totalValueInput = document.getElementById('total_value');
    
    function updateTiposDisponiveis() {
        const entryId = entrySelect.value;
        
        if (!entryId) {
            roomTypeSelect.innerHTML = '<option value="">Selecione a data de entrada primeiro</option>';
            return;
        }
        
        roomTypeSelect.innerHTML = '<option value="">Carregando tipos disponíveis...</option>';
        
        fetch(`/api/tipos_disponiveis?entry_date=${entryId}&exit_date=${exitSelect.value}`)
            .then(response => response.json())
            .then(tipos => {
                roomTypeSelect.innerHTML = tipos.length > 0 
                    ? '<option value="">Selecione um tipo</option>'
                    : '<option value="">Nenhum tipo disponível para estas datas</option>';
                
                tipos.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo;
                    option.textContent = `Tipo ${tipo} (R$ ${PRECOS[tipo]}/dia)`;
                    roomTypeSelect.appendChild(option);
                });
                
                if (roomTypeSelect.dataset.prevValue) {
                    const prevOption = roomTypeSelect.querySelector(`option[value="${roomTypeSelect.dataset.prevValue}"]`);
                    if (prevOption) {
                        prevOption.selected = true;
                    }
                }
                
                calcularPreco();
            })
            .catch(error => {
                console.error('Erro:', error);
                roomTypeSelect.innerHTML = '<option value="">Erro ao carregar tipos</option>';
            });
    }
    


    function calcularPreco() {
        const tipoQuarto = roomTypeSelect.value;
        const entrada = entrySelect.value;
        const saida = exitSelect.value;
        
        if (!tipoQuarto || !entrada || !saida) {
            valorTotalSpan.textContent = 'R$ 0,00';
            totalValueInput.value = '0';
            return;
        }
        
        const entradaText = entrySelect.options[entrySelect.selectedIndex].text;
        const saidaText = exitSelect.options[exitSelect.selectedIndex].text;
        
        const [diaEntrada, mesEntrada, anoEntrada] = entradaText.split('/').map(Number);
        const [diaSaida, mesSaida, anoSaida] = saidaText.split('/').map(Number);
        
        const dataEntrada = new Date(anoEntrada, mesEntrada - 1, diaEntrada);
        const dataSaida = new Date(anoSaida, mesSaida - 1, diaSaida);
        
        const diffTime = dataSaida - dataEntrada;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
        
        if (diffDays <= 0) {
            valorTotalSpan.textContent = 'Datas inválidas';
            totalValueInput.value = '0';
            return;
        }
        
        const precoDiaria = PRECOS[tipoQuarto] || 0;
        const total = precoDiaria * diffDays;
        
        totalValueInput.value = total;
        
        valorTotalSpan.textContent = total.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
    }
    


    function atualizarDataSaida() {
        if (!entrySelect.value) return;
        
        const entradaText = entrySelect.options[entrySelect.selectedIndex].text;
        const [dia, mes, ano] = entradaText.split('/').map(Number);
        
        const dataMinima = new Date(ano, mes - 1, dia + 1);
        const dataMinimaStr = dataMinima.toLocaleDateString('pt-BR');
        
        exitSelect.innerHTML = '';
        
        const todasDatas = Array.from(entrySelect.options)
            .filter(opt => opt.value)
            .map(opt => ({id: opt.value, data: opt.text}));
        
        const dataEntrada = new Date(ano, mes - 1, dia);
        
        todasDatas.forEach(opt => {
            const [d, m, a] = opt.data.split('/').map(Number);
            const dataOpt = new Date(a, m - 1, d);
            
            if (dataOpt > dataEntrada) {
                const option = document.createElement('option');
                option.value = opt.id;
                option.textContent = opt.data;
                exitSelect.appendChild(option);
                
                if (opt.data === dataMinimaStr) {
                    option.selected = true;
                }
            }
        });
        
        calcularPreco();
    }
    
    roomTypeSelect.addEventListener('change', function() {
        this.dataset.prevValue = this.value;
        calcularPreco();
    });
    
    entrySelect.addEventListener('change', function() {
        atualizarDataSaida();
        updateTiposDisponiveis();
    });
    
    exitSelect.addEventListener('change', function() {
        calcularPreco();
        updateTiposDisponiveis();
    });
});